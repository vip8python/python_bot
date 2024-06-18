from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from database import DataBase
from models import User


class RegistrationMiddleware(BaseMiddleware):
    def __init__(self, allowed_commands):
        self.allowed_commands = allowed_commands
        super().__init__()

    async def __call__(self, handler, event: Message, data: dict):
        command = event.text.split()[0]
        if command not in self.allowed_commands:
            return await handler(event, data)

        telegram_id = event.from_user.id
        async with DataBase().Session() as session:
            query = select(User).where(User.telegram_id == str(telegram_id))
            user = await session.execute(query)
            user = user.scalar_one_or_none()

            if not user:
                await event.answer("You need to be registered to create tasks. Please use /register to register.")
                return
        return await handler(event, data)


def get_registration_middleware(commands):
    return RegistrationMiddleware(commands)
