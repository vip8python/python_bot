from datetime import datetime


async def is_integer(value: str) -> bool:
    try:
        int_value = int(value)
        return int_value > 0
    except ValueError:
        return False


async def validate_date(message, state, field_name):
    try:
        user_date = datetime.strptime(message.text, '%Y-%m-%d')
        if user_date < datetime.now():
            await message.answer(f"{field_name.capitalize()} date cannot be in the past. Please enter a future date.")
            return False
        await state.update_data({field_name: user_date.strftime('%Y-%m-%d')})
        return True
    except ValueError:
        await message.answer(f"Please enter a valid date in YYYY-MM-DD format.")
        return False


async def validate_end_date(start_date: str, end_date: str) -> bool:
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        return end_dt > start_dt
    except ValueError:
        return False

