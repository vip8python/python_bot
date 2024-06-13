import os
from Database.models import User, Project, Admin, Category, Qualification, ProjectEmployee
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DataBase:
    def __init__(self) -> None:
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        self.connect = f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.async_engine = create_async_engine(self.connect, echo=True)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)

    async def __aenter__(self):
        self.session = self.Session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()

    async def get_admin(self, admin_id: int) -> Optional[Admin]:
        async with self.Session() as session:
            result = await session.execute(select(Admin).where(Admin.telegram_id == str(admin_id)))
        return result.scalar()

    # Async funkcijos dalyvių pridėjimui ir pašalinimui
    async def add_participant_to_project(self, project_id: int, user: User, current_user_id: int):
        async with self.Session() as session:
            async with session.begin():
                project = await session.get(Project, project_id)
                if project.creator_id != current_user_id:
                    raise PermissionError("Only the project creator can add participants.")

                project.add_participant(user)
                session.add(project)  # pridėkite projekto atnaujinimus į sesiją

    async def remove_participant_from_project(self, project_id: int, user: User, current_user_id: int):
        async with self.Session() as session:
            async with session.begin():
                project = await session.get(Project, project_id)
                if project.creator_id != current_user_id:
                    raise PermissionError("Only the project creator can remove participants.")

                project.remove_participant(user)
                session.add(project)  # pridėkite projekto atnaujinimus į sesiją

    async def get_all_categories(self) -> Sequence[Category]:
        async with self.Session() as session:
            result = await session.scalars(select(Category))
        return result.all()

    async def get_qualifications(self):
        print('qualification db')
        async with self.Session() as session:
            result = await session.scalars(select(Qualification))
        return result.all()

    async def create_task(self, title, description, start_time, end_time, hourly_rate, participants_needed, repository_url,
                          creator_id, category_id, employees_data):
        async with self.Session() as session:
            async with session.begin():
                new_task = Project(
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    hourly_rate=hourly_rate,
                    participants_needed=participants_needed,
                    repository_url=repository_url,
                    creator_id=creator_id,
                    category_id=category_id
                )
                session.add(new_task)
                await session.flush()  # To get the new_task.id

                for emp_data in employees_data:
                    new_employee = ProjectEmployee(
                        project_id=new_task.id,
                        employees_count=emp_data['employees_count'],
                        qualification_id=emp_data['qualification_id']
                    )
                    session.add(new_employee)
                await session.commit()

    async def get_tasks_by_category(self, category_id):
        async with self.Session() as session:
            result = await session.execute(
                select(Project).where(Project.category_id == category_id)
            )
            return result.scalars().all()