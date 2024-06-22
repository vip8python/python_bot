import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging.config
from models import Project, Admin, Category, Qualification, ProjectQualificationEmployee, User, SalaryType
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

logger = logging.getLogger(__name__)


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

    async def get_all_categories(self) -> Sequence[Category]:
        async with self.Session() as session:
            result = await session.scalars(select(Category))
        return result.all()

    async def get_qualifications(self):
        async with self.Session() as session:
            result = await session.scalars(select(Qualification))
        return result.all()

    async def get_tasks_by_category(self, category_id):
        async with self.Session() as session:
            result = await session.execute(
                select(Project).where(Project.category_id == category_id)
            )
            return result.scalars().all()

    async def get_salary_options(self):
        async with self.Session() as session:
            result = await session.scalars(select(SalaryType))
        return result.all()

    async def get_async_session(self):
        async with self.Session() as session:
            yield session

    async def is_user_registered(self, telegram_id: str) -> Optional[User]:
        async with self.Session() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_qualification(session: AsyncSession, qualification_name: str) -> int:
        result = await session.execute(
            select(Qualification).filter_by(name=qualification_name)
        )
        qualification = result.scalar_one_or_none()
        if not qualification:
            qualification = Qualification(name=qualification_name)
            session.add(qualification)
            await session.flush()
        return qualification.id

    async def save_task_to_db(self, session: AsyncSession, title: str, description: str, start_date: str,
                              end_date: str, employees_list: list, full_price: int, repository_url: str,
                              telegram_id: str, category_id: int, salary_type_id: int) -> Project:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        user = await self.is_user_registered(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found.")
        creator_id = user.id

        new_project = Project(
            title=title,
            description=description,
            start_time=start_date,
            end_time=end_date,
            salary=full_price,
            participants_needed=sum([e['employees_count'] for e in employees_list]),
            repository_url=repository_url,
            creator_id=creator_id,
            category_id=category_id
        )
        session.add(new_project)
        await session.flush()
        for employee in employees_list:
            qualification_id = await self.get_or_create_qualification(session, employee['qualification']['name'])
            new_employee = ProjectQualificationEmployee(
                project_id=new_project.id,
                employees_count=employee['employees_count'],
                qualification_id=qualification_id,
                salary_types_id=salary_type_id,
                amount=employee['salary'],
                currency='EUR'
            )
            session.add(new_employee)
        await session.commit()
        return new_project

    async def create_user(self, session: AsyncSession, username: str, contacts: str, description: str,
                          telegram_id: str, experience: int, skills_list: list, country: str, languages_list: list,
                          registered: datetime) -> User:
        try:
            existing_user = await self.is_user_registered(telegram_id)
            if existing_user:
                raise Exception(f"User with telegram_id already exists.")

            new_user = User(
                username=username,
                contacts=contacts,
                description=description,
                telegram_id=telegram_id,
                registered=registered,
                experience=experience,
                skills=json.dumps(skills_list),
                rating=0.0,
                country=country,
                languages=json.dumps(languages_list)
            )
            session.add(new_user)
            try:
                await session.commit()
            except Exception as e:
                logger.error(f'error {e}')
            return new_user
        except Exception as e:
            logger.error(f'Error in create_user: {e}', exc_info=True)
            raise
        finally:
            await session.close()
