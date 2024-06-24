from aiogram.fsm.state import StatesGroup, State


class UpdateUserForm(StatesGroup):
    waiting_for_field = State()
    waiting_for_value = State()
    waiting_for_experience = State()
    waiting_for_skills_action = State()
    waiting_for_update_skill = State()
    waiting_for_update_skill_experience = State()
    waiting_for_skill = State()
    waiting_for_skill_experience = State()
    waiting_for_new_language = State()
    waiting_for_new_languages = State()
