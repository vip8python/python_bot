import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from database import DataBase
from keyboards.registration_kb import enter_and_finish_kb, skill_kb, language_list_kb
from states.registration import RegisterUser
from utils.validators import is_integer

router = Router()
storage = MemoryStorage()
db = DataBase()


@router.message(F.text == '/register')
async def start_registration(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    is_registered = await db.is_user_registered(telegram_id)
    if is_registered:
        await message.answer('You are registered')
    else:
        await message.answer('Please enter your username:')
        await state.set_state(RegisterUser.username)


@router.message(RegisterUser.username)
async def enter_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Please enter your contact information:')
    await state.set_state(RegisterUser.contacts)


@router.message(RegisterUser.contacts)
async def enter_contacts(message: Message, state: FSMContext):
    await state.update_data(contacts=message.text)
    await message.answer('Please enter a short description about yourself:')
    await state.set_state(RegisterUser.description)


@router.message(RegisterUser.description)
async def enter_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('If you have programming experience and want to be seen select enter else finish',
                         reply_markup=enter_and_finish_kb)


@router.callback_query(F.data == 'experience_enter')
async def select_enter(call: CallbackQuery, state: FSMContext):
    await call.message.answer('How old is your programming experience?')
    await state.set_state(RegisterUser.experience)


@router.callback_query(F.data.startswith('finish_registration'))
async def finish_registration(call: CallbackQuery, state: FSMContext):
    await finalize_registration(call.message, state)


@router.message(RegisterUser.experience)
async def add_experience(message: Message, state: FSMContext):
    experience = message.text
    if not await is_integer(experience):
        await message.answer("Please enter a valid positive integer for experience.")
        return
    await state.update_data(experience=experience)
    await message.answer('Please enter your first skill')
    await state.set_state(RegisterUser.skills_list)


@router.message(RegisterUser.skills_list)
async def add_skills(message: Message, state: FSMContext):
    skill = message.text
    await state.update_data(skill=skill)
    await message.answer('Please enter your experience time for this skill:')
    await state.set_state(RegisterUser.adding_skill_experience)


@router.message(RegisterUser.adding_skill_experience)
async def add_skill_experience(message: Message, state: FSMContext):
    experience = message.text
    data = await state.get_data()
    skill = data.get('skill')
    if not await is_integer(experience):
        await message.answer("Please enter a valid positive integer for experience.")
        return
    skills_list = data.get('skills_list', [])
    skills_list.append({'skill': skill, 'experience': int(experience)})
    await state.update_data(skills_list=skills_list)
    await message.answer('Your skill added, please enter your next skill or select enter', reply_markup=skill_kb)


@router.callback_query(F.data == 'new_skill')
async def add_more_skills(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter your next skill')
    await state.set_state(RegisterUser.skills_list)


@router.callback_query(F.data == 'skills_finish')
async def finish_skills(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter the country where you live:')
    await state.set_state(RegisterUser.country)


@router.message(RegisterUser.country)
async def add_country(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)
    await message.answer('Please enter the language in which you can communicate:')
    await state.set_state(RegisterUser.languages_list)


@router.message(RegisterUser.languages_list)
async def add_languages(message: Message, state: FSMContext):
    languages = message.text
    data = await state.get_data()
    languages_list = data.get('languages_list', [])
    languages_list.append(languages)
    await state.update_data(languages_list=languages_list)
    await message.answer('Languages added, you can add more language', reply_markup=language_list_kb)


@router.callback_query(F.data == 'add_language')
async def more_language(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter another language:')
    await state.set_state(RegisterUser.languages_list)


@router.callback_query(F.data == 'finish_registration')
async def finish_registration(call: CallbackQuery, state: FSMContext):
    await finalize_registration(call.message, state)


async def finalize_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data.get('username')
    contacts = user_data.get('contacts')
    description = user_data.get('description')
    telegram_id = str(message.chat.id)
    experience = int(user_data.get('experience', 0))
    skills_list = user_data.get('skills_list', [])
    country = user_data.get('country', 'world')
    languages_list = user_data.get('languages_list', [])
    registered = datetime.datetime.utcnow()
    async for session in db.get_async_session():
        try:
            new_user = await db.create_user(session, username, contacts, description, telegram_id, experience,
                                            skills_list, country, languages_list, registered)
            await message.reply(f'Created new user: {new_user.username}')
        except Exception as e:
            await message.answer(f'Error: {e}')
        finally:
            await state.clear()
