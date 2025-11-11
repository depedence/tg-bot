import asyncio
import logging
from aiogram import Bot, Dispatcher

from config.settings import BOT_TOKEN
from bot.handlers import basic, admin
from database.database import init_db
from services.scheduler_service import setup_scheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(basic.router)
    dp.include_router(admin.router)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    logging.info('Бот запущен!')

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
