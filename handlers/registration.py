from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from database import DataBase
from states.registration import RegisterUser

router = Router()
storage = MemoryStorage()
db = DataBase()


@router.message(F.text == '/register')
async def start_registration(message: Message, state: FSMContext):
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
    user_data = await state.get_data()
    username = user_data['username']
    contacts = user_data['contacts']
    description = user_data['description']
    telegram_id = str(message.from_user.id)

    async for session in db.get_async_session():
        try:
            new_user = await db.create_user(session, username, contacts, description, telegram_id)
            await message.reply(f'Created new user: {new_user.username}')
        except Exception as e:
            await message.answer(f'Error: {e}')
        finally:
            await state.clear()
