import asyncio
import logging
import logging.config
import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv
from Core.Logging.formatters import CustomJsonFormatter
from Core.menu import set_commands

load_dotenv()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'main_formatter': {
            'format': os.getenv('FORMAT'),
            'style': '{'
        },
        'json_formatter': {
            '()': CustomJsonFormatter,
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter'
        },
        'main': {
            'class': 'logging.FileHandler',
            'filename': os.getenv('LOG_FILE_PATH'),
            'formatter': 'json_formatter',
        },
    },

    'loggers': {
        'main': {
            'handlers': ['main', 'console'],
            'propagate': True,
            'level': os.getenv('LEVEL_NAME')
        }

    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main')

token = os.getenv('TOKEN')
if not token:
    raise ValueError('Not found token_id')
bot_ = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    try:
        logger.info('Starting bot ...')
        await set_commands(bot_)
        await dp.start_polling(bot_, skip_updates=True)
    except Exception as e:
        logging.error(f'error : {e}', exc_info=True)
    finally:
        await bot_.session.close()
        logger.info('Bot stopped.')


if __name__ == '__main__':
    asyncio.run(main())
