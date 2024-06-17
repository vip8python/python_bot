from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from database import DataBase
from models import User


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        telegram_id = event.from_user.id

        async with DataBase().get_async_session() as session:
            query = select(User).where(User.telegram_id == str(telegram_id))
            user = await session.execute(query)
            user = user.scalar_one_or_none()

            if user is None:
                await event.answer("You need to be registered to create tasks. Please use /register to register.")
                return

        return await handler(event, data)
