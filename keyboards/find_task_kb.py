from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import DataBase


async def find_all_categories_kb():
    async with DataBase() as db:
        categories = await db.get_all_categories()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name,
                                          callback_data=f'find_category_{category.id}'))
    return keyboard.adjust(2).as_markup()
