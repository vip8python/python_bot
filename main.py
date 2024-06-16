import asyncio
import logging
import logging.config
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from core.logging.formatters import CustomJsonFormatter
from core.menu import set_commands
from models import Base
from handlers.create_task import router as create_router
from handlers.start import router as start_router
from handlers.find_task import router as find_router

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
    raise ValueError('Not found token')
bot_ = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def create_tables():
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    connect = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_async_engine(connect, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def main():
    dp.include_routers(
        create_router,
        start_router,
        find_router
    )
    try:
        logger.info('Starting bot ...')
        # await create_tables()
        await set_commands(bot_)
        await dp.start_polling(bot_, skip_updates=True)
    except Exception as e:
        logging.error(f'error : {e}', exc_info=True)
    finally:
        await bot_.session.close()
        logger.info('Bot stopped.')


if __name__ == '__main__':
    asyncio.run(main())
