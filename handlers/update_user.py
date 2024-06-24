import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from database import DataBase
from keyboards.update_task_kb import user_update_categories, skills_update_options, languages_update_options, \
    skill_experience_kb
from states.update_state import UpdateUserForm
from utils.validators import is_integer

logger = logging.getLogger('main')
router = Router()
storage = MemoryStorage()
db = DataBase()


@router.message(F.text == '/update_user')
async def start_update(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    is_registered = await db.is_user_registered(telegram_id)
    if not is_registered:
        await message.answer('You are not registered')
    else:
        await message.answer('Please select the field you want to update:', reply_markup=user_update_categories)
        await state.set_state(UpdateUserForm.waiting_for_field)


@router.callback_query(F.data.startswith('update_experience'))
async def update_experience_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter your experience (number of years):')
    await state.set_state(UpdateUserForm.waiting_for_experience)


@router.message(UpdateUserForm.waiting_for_experience)
async def process_experience_update(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer('Please enter a valid positive integer')
        return
    experience = int(message.text)
    telegram_id = str(message.from_user.id)
    await db.update_user_field(telegram_id, 'experience', experience)
    await message.answer(f'Your experience has been updated to {experience} years.')
    await state.clear()


@router.callback_query(F.data.startswith('update_'))
async def process_field_selection(call: CallbackQuery, state: FSMContext):
    await call.answer()
    field = call.data.split('_')[1]
    await state.update_data(field=field)
    if field == 'skills':
        await call.message.answer('Do you want to add a new skill or update existing ones?',
                                  reply_markup=skills_update_options)
        await state.set_state(UpdateUserForm.waiting_for_skills_action)
    elif field == 'languages':
        await call.message.answer('Do you want to add a new language or update existing ones?',
                                  reply_markup=languages_update_options)
    else:
        await call.message.answer(f'Please enter the new value for {field}:')
        await state.set_state(UpdateUserForm.waiting_for_value)


@router.callback_query(F.data == 'add_skill')
async def add_skill(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Please enter the new skill:')
    await state.set_state(UpdateUserForm.waiting_for_skill)


@router.message(UpdateUserForm.waiting_for_skill)
async def add_skill_experience(message: Message, state: FSMContext):
    skill = message.text
    await state.update_data(skill=skill)
    await message.answer('Enter skill experience time(integer):')
    await state.set_state(UpdateUserForm.waiting_for_skill_experience)


@router.message(UpdateUserForm.waiting_for_skill_experience)
async def process_skill_experience(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer('Please enter a valid positive integer:')
        return
    skill_experience = int(message.text)
    data = await state.get_data()
    skill = data.get('skill')
    telegram_id = str(message.from_user.id)
    new_skill = {skill: skill_experience}
    await db.update_user_field(telegram_id, 'skills', [new_skill])
    await message.answer(f'Skill {skill} with experience {skill_experience} has been added.'
                         f'Select more skill or finish', reply_markup=skill_experience_kb)
    await state.clear()


@router.callback_query(F.data == 'add_skills')
async def update_skills(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Please enter the new skill:')
    await state.set_state(UpdateUserForm.waiting_for_update_skill)


@router.message(UpdateUserForm.waiting_for_update_skill)
async def add_skill_to_existing(message: Message, state: FSMContext):
    skill = message.text
    await state.update_data(skill=skill)
    await message.answer('Enter skill experience time (integer):')
    await state.set_state(UpdateUserForm.waiting_for_update_skill_experience)


@router.message(UpdateUserForm.waiting_for_update_skill_experience)
async def process_update_skill_experience(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer('Please enter a valid positive integer:')
        return
    skill_experience = int(message.text)
    data = await state.get_data()
    skill = data.get('skill')
    telegram_id = str(message.from_user.id)
    current_skills = await db.get_user_field(telegram_id, 'skills') or []
    new_skill = {skill: skill_experience}
    current_skills.append(new_skill)
    await db.update_user_field(telegram_id, 'skills', current_skills)
    await message.answer(f'Skill {skill} with experience {skill_experience} has been added.\n'
                         f'Select more skill or finish', reply_markup=skill_experience_kb)
    await state.clear()


@router.callback_query(F.data == 'add_new_language')
async def add_language(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Please enter the new language:')
    await state.set_state(UpdateUserForm.waiting_for_new_language)


@router.callback_query(F.data == "new_languages")
async def update_languages_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter your languages (comma separated):")
    await state.set_state(UpdateUserForm.waiting_for_new_languages)


@router.message(UpdateUserForm.waiting_for_new_language)
async def process_new_language(message: Message, state: FSMContext):
    languages = message.text.split(',')
    languages = [lang.strip() for lang in languages]
    telegram_id = str(message.from_user.id)
    await db.update_user_field(telegram_id, 'languages', languages)
    await message.answer(f'Languages have been updated to: {", ".join(languages)}.')
    await state.clear()


@router.message(UpdateUserForm.waiting_for_new_languages)
async def process_new_languages(message: Message, state: FSMContext):
    languages = message.text.split(',')
    languages = [lang.strip() for lang in languages]
    telegram_id = str(message.from_user.id)
    current_languages = await db.get_user_field(telegram_id, 'languages') or []
    if not isinstance(current_languages, list):
        current_languages = []
    current_languages.extend(languages)
    await db.update_user_field(telegram_id, 'languages', current_languages)
    await message.answer(f'Languages have been updated to: {", ".join(current_languages)}.')
    await state.clear()


@router.message(UpdateUserForm.waiting_for_value)
async def process_value_input(message: Message, state: FSMContext):
    new_value = message.text
    user_data = await state.get_data()
    field = user_data['field']
    telegram_id = str(message.from_user.id)
    await db.update_user_field(telegram_id, field, new_value)
    await message.answer(f'{field} has been updated to: {new_value}.')
    await state.clear()


@router.callback_query(F.data == 'finish_update')
async def finish_update(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Your updates have been saved.')
    await state.clear()
