from aiogram.fsm.state import State, StatesGroup


class RegisterUser(StatesGroup):
    username = State()
    contacts = State()
    description = State()
    experience = State()
    skills_list = State()
    adding_skill_experience = State()
    country = State()
    languages_list = State()

