from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import DataBase


async def all_categories_kb():
    async with DataBase() as db:
        categories = await db.get_all_categories()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name,
                                          callback_data=f'category_{category.id}_{category.name}'))
    return keyboard.adjust(2).as_markup()


async def all_qualification_kb():
    async with DataBase() as db:
        qualifications = await db.get_qualifications()
    keyboard = InlineKeyboardBuilder()
    for qualification in qualifications:
        keyboard.add(InlineKeyboardButton(text=qualification.name,
                                          callback_data=f'qualification_{qualification.id}_{qualification.name}'))
    return keyboard.adjust(2).as_markup()


async def add_more_employees_kb():
    items = ['more_employees', 'next_step']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=item, callback_data=item)
    return builder.adjust(1).as_markup()


async def salary_options_kb():
    async with DataBase() as db:
        options = await db.get_salary_options()
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.add(InlineKeyboardButton(text=option.name,
                                         callback_data=f'category_{option.id}_{option.name}'))
    return builder.adjust(2).as_markup()


async def get_employees_kb(employees_list):
    keyboard = InlineKeyboardBuilder()
    for idx, employee in enumerate(employees_list):
        keyboard.add(InlineKeyboardButton(
            text=f"{employee['employees_count']} {employee['qualification']['name']}",
            callback_data=f'employee_{idx}'
        ))
    return keyboard.adjust(1).as_markup()
