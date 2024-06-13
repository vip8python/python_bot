from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class CreateTask(StatesGroup):
    framework = State()
    name = State()
    qualification = State()
    number_of_employees = State()
    start_date = State()
    end_date = State()
    salary = State()
    platform_address = State()
