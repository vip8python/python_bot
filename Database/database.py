import os
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from Database.models import Admins, User, Project, Base


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

    async def __aenter__(self) -> 'DataBase':
        self.session = await self.Session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()



    async def get_admin(self, admin_id: int) -> Optional[Admins]:
        async with self.Session() as session:
            result = await session.execute(select(Admins).where(Admins.telegram_id == str(admin_id)))
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
