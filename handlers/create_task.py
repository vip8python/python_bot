from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

from keyboards.create_task_kb import all_categories_kb, all_qualification_kb, add_more_employees_kb
from states.create_task_state import CreateTask

router = Router()
storage = MemoryStorage()


@router.message(F.text == 'create task')
async def categories(message: Message, state: FSMContext):
    await message.answer('Frameworks', reply_markup=await all_categories_kb())
    await state.set_state(CreateTask.framework)


@router.callback_query(F.data.startswith('category_'))
async def category_selected(call: CallbackQuery, state: FSMContext):
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


@router.callback_query(CreateTask.qualification, F.data.startswith('qualification_'))
async def qualification_selected(call: CallbackQuery, state: FSMContext):
    qualification_id = int(call.data.split('_')[1])
    qualification_name = call.data.split('_')[-1]
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    employees_list.append({'employees_count': 0, 'qualification': {'id': qualification_id, 'name': qualification_name}})
    await state.update_data(employees_list=employees_list)
    await call.message.answer(f'You selected {qualification_name}. Please enter the number of employees.')
    await state.set_state(CreateTask.number_of_employees)


@router.message(CreateTask.number_of_employees)
async def enter_number_of_employees(message: Message, state: FSMContext):
    employees_count = int(message.text)
    data = await state.get_data()
    employees_list = data.get('employees_list', [])
    if employees_list and employees_list[-1]['employees_count'] == 0:
        employees_list[-1]['employees_count'] = employees_count
    await state.update_data(employees_list=employees_list)
    employees_info = ", ".join([f"{e['employees_count']} {e['qualification']['name']}" for e in employees_list])
    await message.answer(f'You have {employees_info} employees.', reply_markup=await add_more_employees_kb())


@router.callback_query(F.data == 'more_employees')
async def more_employees_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter more qualification', reply_markup=await all_qualification_kb())
    await state.set_state(CreateTask.qualification)


@router.callback_query(F.data == 'next_step')
async def next_step_selected(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Please enter the start date.')
    await state.set_state(CreateTask.start_date)


@router.message(CreateTask.start_date)
async def enter_start_date(message: Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await message.answer('Please enter the end date.')
    await state.set_state(CreateTask.end_date)


@router.message(CreateTask.end_date)
async def enter_end_date(message: Message, state: FSMContext):
    await state.update_data(end_date=message.text)
    await message.answer('Please enter the salary.')
    await state.set_state(CreateTask.salary)


@router.message(CreateTask.salary)
async def reward(message: Message, state: FSMContext):
    await state.update_data(reward=message.text)
    await message.answer('Please enter the platform address.')
    await state.set_state(CreateTask.platform_address)


@router.message(CreateTask.platform_address)
async def enter_platform_address(message: Message, state: FSMContext):
    await state.update_data(platform_address=message.text)
    data = await state.get_data()
    name = data.get('name')
    employees_list = data.get('employees_list', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    salary = data.get('salary')
    platform_address = data.get('platform_address')

    employees_info = "\n".join(
        [f"{e['employees_count']} employees with qualification: {e['qualification']['name']}" for e in employees_list])

    response = (f"Task created with the following details:\n"
                f"Task Name: {name}\n"
                f"Employees:\n{employees_info}\n"
                f"Start Date: {start_date}\n"
                f"End Date: {end_date}\n"
                f"Reward: {salary}\n"
                f"Platform Address: {platform_address}")

    await message.answer(response)
    await state.clear()
