from aiogram.fsm.state import State, StatesGroup


class CreateTask(StatesGroup):
    category = State()
    title = State()
    description = State()
    qualification = State()
    number_of_employees = State()
    salary = State()
    project_price = State()
    start_date = State()
    end_date = State()
    repository_url = State()
