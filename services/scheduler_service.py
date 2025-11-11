"""
Сервис для автоматической рассылки квестов по расписанию.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from sqlalchemy import select
from database.database import async_session_maker
from database.models import User
from database.crud import create_ai_quest_for_user
import json
import logging

logger = logging.getLogger(__name__)


async def send_daily_quests(bot: Bot):
    """
    Генерирует и отправляет ежедневные квесты всем пользователям.
    Вызывается каждый день в 9:00.
    """
    logger.info("🔄 Начинаем генерацию ежедневных квестов...")

    async with async_session_maker() as session:
        # Получаем всех пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            try:
                # Генерируем квест через AI
                quest = await create_ai_quest_for_user(
                    session=session,
                    user=user,
                    quest_type="daily"
                )

                # Парсим задания из JSON
                tasks = json.loads(quest.tasks)
                tasks_text = "\n".join([f"  • {task}" for task in tasks])

                # Формируем сообщение
                difficulty_emoji = {
                    "easy": "🟢",
                    "medium": "🟡",
                    "hard": "🔴"
                }
                emoji = difficulty_emoji.get(quest.difficulty, "⚪")

                message = (
                    f"⚔️ **НОВЫЙ ЕЖЕДНЕВНЫЙ КВЕСТ** ⚔️\n\n"
                    f"{emoji} **{quest.title}**\n\n"
                    f"📜 {quest.description}\n\n"
                    f"📋 **Задания:**\n{tasks_text}\n\n"
                    f"💪 Сложность: {quest.difficulty.upper()}\n\n"
                    f"Используй /my_quests чтобы увидеть все квесты."
                )

                # Отправляем квест пользователю
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode="Markdown"
                )

                logger.info(f"✅ Отправлен дейли квест пользователю {user.telegram_id}")

            except Exception as e:
                logger.error(f"❌ Ошибка при создании квеста для {user.telegram_id}: {e}")

    logger.info("✅ Генерация ежедневных квестов завершена")


async def send_weekly_quests(bot: Bot):
    """
    Генерирует и отправляет недельные квесты всем пользователям.
    Вызывается каждый понедельник в 9:00.
    """
    logger.info("🔄 Начинаем генерацию недельных квестов...")

    async with async_session_maker() as session:
        # Получаем всех пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            try:
                # Генерируем квест через AI
                quest = await create_ai_quest_for_user(
                    session=session,
                    user=user,
                    quest_type="weekly"
                )

                # Парсим задания из JSON
                tasks = json.loads(quest.tasks)
                tasks_text = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(tasks)])

                # Формируем сообщение
                difficulty_emoji = {
                    "medium": "🟡",
                    "hard": "🔴"
                }
                emoji = difficulty_emoji.get(quest.difficulty, "🔴")

                message = (
                    f"🏆 **НОВЫЙ НЕДЕЛЬНЫЙ КВЕСТ** 🏆\n\n"
                    f"{emoji} **{quest.title}**\n\n"
                    f"📜 {quest.description}\n\n"
                    f"📋 **Задания на неделю:**\n{tasks_text}\n\n"
                    f"💪 Сложность: {quest.difficulty.upper()}\n\n"
                    f"У тебя 7 дней чтобы доказать свою силу!\n"
                    f"Используй /my_quests чтобы увидеть все текущие квесты."
                )

                # Отправляем квест пользователю
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode="Markdown"
                )

                logger.info(f"✅ Отправлен недельный квест пользователю {user.telegram_id}")

            except Exception as e:
                logger.error(f"❌ Ошибка при создании недельного квеста для {user.telegram_id}: {e}")

    logger.info("✅ Генерация недельных квестов завершена")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """
    Настраивает и запускает scheduler для автоматической рассылки квестов.

    Args:
        bot: Экземпляр бота для отправки сообщений

    Returns:
        Настроенный scheduler
    """
    scheduler = AsyncIOScheduler()

    # Ежедневные квесты - каждый день в 9:00
    scheduler.add_job(
        send_daily_quests,
        trigger=CronTrigger(hour=9, minute=0),
        args=[bot],
        id="daily_quests",
        name="Рассылка ежедневных квестов",
        replace_existing=True
    )

    # Недельные квесты - каждый понедельник в 9:00
    scheduler.add_job(
        send_weekly_quests,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
        args=[bot],
        id="weekly_quests",
        name="Рассылка недельных квестов",
        replace_existing=True
    )

    logger.info("📅 Scheduler настроен:")
    logger.info("   - Ежедневные квесты: каждый день в 9:00")
    logger.info("   - Недельные квесты: каждый понедельник в 9:00")

    return scheduler
