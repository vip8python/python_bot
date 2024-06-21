from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardButton

enter_and_finish_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='enter', callback_data='experience_enter'),
        InlineKeyboardButton(text='finish', callback_data='finish_registration')
    ]
])

skill_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='next skill', callback_data='new_skill'),
        InlineKeyboardButton(text='enter', callback_data='skills_finish')
    ]])

language_list_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='add language', callback_data='add_language'),
        InlineKeyboardButton(text='enter', callback_data='finish_registration')
    ]])
