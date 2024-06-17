from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Start bot'
        ),
        BotCommand(
            command='register',
            description='Registration'
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
            command='help',
            description='Help'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
