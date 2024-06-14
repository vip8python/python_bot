from aiogram.fsm.state import State, StatesGroup


class CreateTask(StatesGroup):
    framework = State()
    name = State()
    qualification = State()
    number_of_employees = State()
    salary = State()
    start_date = State()
    end_date = State()
    platform_address = State()
