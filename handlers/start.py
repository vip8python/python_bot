from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.start_kb import start_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=start_kb)
