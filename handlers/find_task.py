import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import DataBase
from keyboards.find_task_kb import find_all_categories_kb
from models import Project, ProjectQualificationEmployee

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text.in_(['find task', '/find_task']))
async def find_projects(message: Message):
    await message.answer(f'Select a category to search', reply_markup=await find_all_categories_kb())


@router.callback_query(F.data.startswith('find_category_'))
async def find_result(call: CallbackQuery):
    category_id = int(call.data.split('_')[-1])
    projects = []
    async for session in DataBase().get_async_session():
        try:
            result = await session.execute(
                select(Project).options(
                    selectinload(Project.qualifications).selectinload(ProjectQualificationEmployee.qualification),
                    selectinload(Project.qualifications).selectinload(ProjectQualificationEmployee.salary_type)
                ).where(Project.category_id == category_id)
            )
            projects = result.scalars().all()
        except Exception as e:
            logger.error(f'Error: {e}')

    if projects:
        projects_list = '\n'.join(
            [f'Project: {project.title}\n'
             f'Description: {project.description}\n'
             f'Price: {project.salary}eur.\n'
             f'Data: from {project.start_time} to {project.end_time}\n'
             f'Workers needed: {project.participants_needed}\n'
             f'Repository: {project.repository_url}\n'
             f'Employees:\n' + ''.join(
                [f'{employee.employees_count} employees with qualification: {employee.qualification.name}\n'
                 f'Salary: {employee.amount}{employee.currency} - {employee.salary_type.name}\n'
                 for employee in project.qualifications]
            ) for project in projects]
        )
        await call.message.answer(f'Found projects:\n{projects_list}\n')
    else:
        logger.error('No projects found')
        await call.message.answer('No projects found for the selected category.')
