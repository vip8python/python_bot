import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message
from database import DataBase


logger = logging.getLogger('info')


class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message):
        try:
            async with DataBase() as db:
                return await db.get_admin(message.from_user.id)
        except Exception as e:
            logger.info(f'Error checking admin status: {e}')
            return None
