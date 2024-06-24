from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from database import DataBase
from keyboards.start_kb import start_kb, start_register_kb
from models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = str(message.from_user.id)
    async for session in DataBase().get_async_session():
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            await message.answer('You need to be registered', reply_markup=start_register_kb)
            return
        await message.answer('Hello', reply_markup=start_kb)


@router.message(F.text == '/help')
async def help_command(message: Message):
    help_text = 'Discussions about the program in the facebook group:'
    facebook_button = InlineKeyboardButton(text='Go to Facebook', url='https://www.facebook.com/groups/279957348446455')
    facebook_markup = InlineKeyboardMarkup(inline_keyboard=[[facebook_button]])
    await message.answer(help_text, reply_markup=facebook_markup)
