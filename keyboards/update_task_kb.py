from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_update_categories = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='username', callback_data='update_username'),
        InlineKeyboardButton(text='contacts', callback_data='update_contacts')],
    [
        InlineKeyboardButton(text='description', callback_data='update_description'),
        InlineKeyboardButton(text='experience', callback_data='update_experience')],
    [
        InlineKeyboardButton(text='skills', callback_data='update_skills'),
        InlineKeyboardButton(text='country', callback_data='update_country')],
    [
        InlineKeyboardButton(text='languages', callback_data='update_languages'),
        InlineKeyboardButton(text='finish', callback_data='finish_update')]
])

skills_update_options = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Delete and enter another skill', callback_data='add_skill')],
    [
        InlineKeyboardButton(text='Add more skill', callback_data='add_skills')
     ]
])

languages_update_options = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Add new language', callback_data='add_new_language')],
    [
        InlineKeyboardButton(text='Update existing languages', callback_data='new_languages')
     ]
])

skill_experience_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='add more skill', callback_data='add_skills'),
        InlineKeyboardButton(text='finish', callback_data='finish_update')
    ]
])




