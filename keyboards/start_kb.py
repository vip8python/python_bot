from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='create task'),
        KeyboardButton(text='find task')
    ]
], resize_keyboard=True,
    input_field_placeholder='....',
    one_time_keyboard=True)

start_register_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='register')
    ]
], resize_keyboard=True,
    one_time_keyboard=True)
