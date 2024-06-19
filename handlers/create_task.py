from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import select

from database import DataBase
from keyboards.create_task_kb import all_categories_kb, all_qualification_kb, add_more_employees_kb, salary_options_kb
from models import User
from states.create_task_state import CreateTask
from utils.validators import is_integer, validate_date, validate_end_date

router = Router()
storage = MemoryStorage()
db = DataBase()


@router.message(F.text.in_(['create task', '/create_task']))
async def categories(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    async for session in DataBase().get_async_session():
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalar_one_or_none()
        if user is None:
            await message.answer("You need to be registered to create tasks. Please use /register to register.")
            return
        await message.answer('Select frameworks', reply_markup=await all_categories_kb())
        await state.set_state(CreateTask.category)


@router.callback_query(CreateTask.category)
async def select_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[1])
    category = call.data.split('_')[-1]
    await call.message.answer(f'You selected {category}. Enter the task name.')
    await state.update_data(category_id=category_id)
    await state.update_data(category=category)
    await state.set_state(CreateTask.title)


@router.message(CreateTask.title)
async def enter_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Write a short description and contacts.')
    await state.set_state(CreateTask.description)


@router.message(CreateTask.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Select what qualification employees are needed.',
                         reply_markup=await all_qualification_kb())
    await state.set_state(CreateTask.qualification)


@router.callback_query(CreateTask.qualification)
async def select_qualification(call: CallbackQuery, state: FSMContext):
    qualification_id = int(call.data.split('_')[1])
    qualification_name = call.data.split('_')[-1]
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    employees_list.append({'employees_count': 0, 'qualification': {'id': qualification_id, 'name': qualification_name}})
    await state.update_data(employees_list=employees_list)
    await call.message.answer(f'You selected {qualification_name}. Please enter the number of employees.')
    await state.set_state(CreateTask.number_of_employees)


@router.message(CreateTask.number_of_employees)
async def enter_number_of_employees(message: Message, state: FSMContext) -> None:
    if not await is_integer(message.text):
        await message.answer("Please enter a valid positive integer for the number of employees.")
    employees_count = int(message.text)
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    if employees_list and employees_list[-1]['employees_count'] == 0:
        employees_list[-1]['employees_count'] = employees_count
    await state.update_data(employees_list=employees_list)
    employees_info = ", ".join([f"{e['employees_count']} {e['qualification']['name']}" for e in employees_list])
    last_employee = f'{employees_list[-1]['employees_count']} {employees_list[-1]['qualification']['name']}'
    await message.answer(f'You have {employees_info} employees. Select salary options for {last_employee}',
                         reply_markup=await salary_options_kb())


@router.callback_query(F.data.startswith('category_'))
async def select_salary_type(call: CallbackQuery, state: FSMContext):
    salary_type = call.data.split('_')[-1]
    salary_type_id = int(call.data.split('_')[-2])
    await state.update_data(salary_type=salary_type)
    await state.update_data(salary_type_id=salary_type_id)
    await call.message.answer(f'Salary option {salary_type} selected. Please enter the salary amount for one.')
    await state.set_state(CreateTask.salary)


@router.message(CreateTask.salary)
async def add_salary(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer("Please enter a valid positive integer for salary.")
        return
    salary = int(message.text)
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    salary_type = data.get('salary_type')
    employees_list[-1]['salary'] = salary
    employees_list[-1]['salary_type'] = salary_type
    await state.update_data(employees_list=employees_list)
    await message.answer(
        f'Salary assigned. Would you like to add more employees or proceed?',
        reply_markup=await add_more_employees_kb())


@router.callback_query(F.data == 'more_employees')
async def next_step_more_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('More employees', reply_markup=await all_qualification_kb())
    await state.set_state(CreateTask.qualification)


@router.callback_query(F.data == 'next_step')
async def next_step_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter the full price for project.')
    await state.set_state(CreateTask.project_price)


@router.message(CreateTask.project_price)
async def project_price(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer("Please enter a valid positive integer for project price.")
    full_price = int(message.text)
    await state.update_data(full_price=full_price)
    await message.answer('Please enter the start date in YYYY-MM-DD format.')
    await state.set_state(CreateTask.start_date)


@router.message(CreateTask.start_date)
async def enter_start_date(message: Message, state: FSMContext):
    if not await validate_date(message, state, 'start_date'):
        return
    start_date = message.text
    await state.update_data(start_date=start_date)
    await message.answer('Please enter the end date in YYYY-MM-DD format.')
    await state.set_state(CreateTask.end_date)


@router.message(CreateTask.end_date)
async def enter_end_date(message: Message, state: FSMContext):
    if not await validate_date(message, state, 'end_date'):
        return
    start_date = (await state.get_data()).get('start_date')
    if not await validate_end_date(start_date, message.text):
        await message.answer("End date should be later than start date. Please enter a valid date.")
    await state.update_data(end_date=message.text)
    await message.answer('Please enter repository address')
    await state.set_state(CreateTask.repository_url)


@router.message(CreateTask.repository_url)
async def enter_repository_address(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    await state.update_data(repository_url=message.text)
    data = await state.get_data()
    title = data.get('title')
    category = data.get('category')
    description = data.get('description')
    employees_list = data.get('employees_list', [])
    full_price = data.get('full_price')
    salary_type_id = int(data.get('salary_type_id'))
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    repository_url = data.get('repository_url')
    category_id = data.get('category_id')

    employees_info = "\n".join(
        [
            f"{e['employees_count']} employees with qualification: {e['qualification']['name']},"
            f" Salary: {e['salary']} - {e['salary_type']}" for e in employees_list])

    response = (f"Task created with the following details:\n"
                f"Task Name: {title}\n"
                f'Category: {category}\n'
                f'Description: {description}\n'
                f"Employees:\n{employees_info}\n"
                f'Full price: {full_price}\n'
                f"Start Date: {start_date}\n"
                f"End Date: {end_date}\n"
                f"Repository Address: {repository_url}")

    await message.answer(response)
    async for session in db.get_async_session():
        await db.save_task_to_db(session, title, description, start_date, end_date, employees_list, full_price,
                                 repository_url, telegram_id, category_id, salary_type_id)
    await state.clear()
