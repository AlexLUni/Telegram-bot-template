import asyncio
import logging
from datetime import datetime

import app.constants as cnst
import pytz
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError
from app.handlers import (
    admin_router,
    callback_router,
    const_router,
    file_router,
    public_commands_router,
    temp_router,
)
from app.helpers import setup_initial_admins
from app.middlewares import init_scheduler_injector, metrics_collector, user_data
from app.scheduler import check_outdated
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from pytz import utc


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Bot launcher."""
    await setup_initial_admins()
    bot = Bot(token=config['bot']['token'])
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone=utc, job_defaults={'misfire_grace_time': cnst.MISFIRE_GRACE_TIME})
    dp.update.middleware(metrics_collector)
    dp.update.middleware(user_data)
    dp.update.middleware(init_scheduler_injector(scheduler))
    logger.info('Starting bot...')
    dp.include_routers(public_commands_router, temp_router, file_router, const_router,
                    admin_router, callback_router)
    scheduler.add_job(check_outdated, trigger='cron', hour=cnst.DELETE_HOUR, minute=cnst.DELETE_MINUTE,
                    start_date=datetime.now(pytz.timezone('Europe/Moscow')))
    scheduler.start()
    try:
        await dp.start_polling(bot, timeout=cnst.POLLING_TIMEOUT, relax=cnst.POLLING_RELAX)
    except TelegramAPIError:
        logger.exception('Telegram API interaction error')
    except TelegramNetworkError:
        logger.exception('Network issues while interacting with Telegram')
    except TimeoutError:
        logger.exception('Timeout while waiting for a response from Telegram API')
    except Exception:
        logger.exception('Unexpected error')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot is shutting down due to keyboard interrupt.')
