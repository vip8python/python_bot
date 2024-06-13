from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def check_admin(db, admin_id):
    admin = await db.get_admin(admin_id)
    return bool(admin)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Start bot'
        ),
        BotCommand(
            command='create_task',
            description='Create task'
        ),
        BotCommand(
            command='find_task',
            description='Find task'
        ),
        BotCommand(
            command='delete_task',
            description='Delete task'
        ),
        BotCommand(
            command='help',
            description='Help'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
