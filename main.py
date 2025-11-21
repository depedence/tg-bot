import asyncio
from aiogram import Bot, Dispatcher
from utils.logger import logger
from config.settings import BOT_TOKEN, DATABASE_TYPE
from bot.handlers import basic, admin, admin_handlers
from database.database import init_db
from services.scheduler_service import setup_scheduler

async def main():
    try:
        # Инициализация БД
        await init_db()
        logger.info("✅ База данных инициализирована (тип: {db_type})", db_type=DATABASE_TYPE)

        # Создание бота и диспетчера
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()

        # Подключение роутеров
        dp.include_router(basic.router)
        dp.include_router(admin.router)
        dp.include_router(admin_handlers.router)

        # Настройка планировщика
        scheduler = setup_scheduler(bot)
        scheduler.start()
        logger.info("📅 Scheduler настроен")

        logger.success("🤖 Бот запущен!")

        # Запуск polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        logger.exception("💥 Критическая ошибка при запуске бота")
        raise
    finally:
        if 'scheduler' in locals():
            scheduler.shutdown()
            logger.info("⏹️ Scheduler остановлен")
        logger.info("👋 Бот остановлен")

if __name__ == '__main__':
    asyncio.run(main())