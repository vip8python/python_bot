from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.start_kb import start_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=start_kb)


@router.message(F.text == '/help')
async def help_command(message: Message):
    help_text = 'Discussions about the program in the facebook group:'
    facebook_button = InlineKeyboardButton(text='Go to Facebook', url='https://www.facebook.com/groups/279957348446455')
    facebook_markup = InlineKeyboardMarkup(inline_keyboard=[[facebook_button]])
    await message.answer(help_text, reply_markup=facebook_markup)
