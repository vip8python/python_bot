from aiogram.fsm.state import State, StatesGroup


class RegisterUser(StatesGroup):
    username = State()
    contacts = State()
    description = State()
