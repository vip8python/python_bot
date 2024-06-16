from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='create task'),
        KeyboardButton(text='find task')
    ]
], resize_keyboard=True,
    input_field_placeholder='....',
    one_time_keyboard=True)
