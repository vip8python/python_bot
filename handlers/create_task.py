from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.create_task_kb import all_categories_kb, all_qualification_kb, add_more_employees_kb, salary_options_kb
from states.create_task_state import CreateTask
from utils.validators import is_integer, validate_date, validate_end_date

router = Router()
storage = MemoryStorage()


@router.message(F.text == 'create task')
async def categories(message: Message, state: FSMContext):
    await message.answer('Frameworks', reply_markup=await all_categories_kb())
    await state.set_state(CreateTask.framework)


@router.callback_query(CreateTask.framework)
async def select_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[1])
    category_name = call.data.split('_')[-1]
    await call.message.answer(f'you selected {category_name}. Enter the task name.')
    await state.update_data(category_id=category_id)
    await state.set_state(CreateTask.name)


@router.message(CreateTask.name)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Select what qualification employees are needed.', reply_markup=await all_qualification_kb())
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
    await message.answer(f'You have {employees_info} employees. Select salary options',
                         reply_markup=await salary_options_kb())


@router.callback_query(F.data.startswith('category_'))
async def select_salary_option(call: CallbackQuery, state: FSMContext):
    price = call.data.split('_')[-1]
    await state.update_data(price=price)
    await call.message.answer(f'Salary option {price} selected. Please enter the salary amount.')
    await state.set_state(CreateTask.salary)


@router.message(CreateTask.salary)
async def add_salary(message: Message, state: FSMContext):
    if not await is_integer(message.text):
        await message.answer("Please enter a valid positive integer for salary.")
        return
    salary = int(message.text)
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    employees_list[-1]['salary'] = salary
    await state.update_data(employees_list=employees_list)
    await message.answer('Salary assigned. Would you like to add more employees or proceed?',
                         reply_markup=await add_more_employees_kb())


@router.callback_query(F.data == 'more_employees')
async def next_step_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('gkhm', reply_markup=await all_qualification_kb())
    await state.set_state(CreateTask.qualification)


@router.callback_query(F.data == 'next_step')
async def next_step_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter the start date in YYYY-MM-DD format.')
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
    await message.answer('Please enter platform address')
    await state.set_state(CreateTask.platform_address)


@router.message(CreateTask.platform_address)
async def enter_platform_address(message: Message, state: FSMContext):
    await state.update_data(platform_address=message.text)
    data = await state.get_data()
    name = data.get('name')
    employees_list = data.get('employees_list', [])
    salary = data.get('price')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    platform_address = data.get('platform_address')

    employees_info = "\n".join(
        [f"{e['employees_count']} employees with qualification: {e['qualification']['name']}, Salary: {e['salary']}" for e in employees_list])

    response = (f"Task created with the following details:\n"
                f"Task Name: {name}\n"
                f"Employees:\n{employees_info}{salary}\n"
                f"Start Date: {start_date}\n"
                f"End Date: {end_date}\n"
                f"Platform Address: {platform_address}")

    await message.answer(response)
    await state.clear()
