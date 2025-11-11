"""
Административные команды для тестирования.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import async_session_maker
from database.crud import get_or_create_user, create_ai_quest_for_user
import json

router = Router()


@router.message(Command("generate_daily"))
async def cmd_generate_daily(message: Message):
    """
    Генерирует дейли квест вручную (для тестирования).
    """
    await message.answer("⏳ Генерирую ежедневный квест...")

    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        try:
            # Генерируем квест
            quest = await create_ai_quest_for_user(
                session=session,
                user=user,
                quest_type="daily"
            )

            # Парсим задания
            tasks = json.loads(quest.tasks)
            tasks_text = "\n".join([f"  • {task}" for task in tasks])

            # Формируем сообщение
            difficulty_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "⚪")

            response = (
                f"⚔️ **НОВЫЙ ЕЖЕДНЕВНЫЙ КВЕСТ** ⚔️\n\n"
                f"{emoji} **{quest.title}**\n\n"
                f"📜 {quest.description}\n\n"
                f"📋 **Задания:**\n{tasks_text}\n\n"
                f"💪 Сложность: {quest.difficulty.upper()}\n\n"
                f"ID квеста: {quest.id}"
            )

            await message.answer(response, parse_mode="Markdown")

        except Exception as e:
            await message.answer(f"❌ Ошибка при генерации квеста: {e}")


@router.message(Command("generate_weekly"))
async def cmd_generate_weekly(message: Message):
    """
    Генерирует недельный квест вручную (для тестирования).
    """
    await message.answer("⏳ Генерирую недельный квест...")

    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        try:
            # Генерируем квест
            quest = await create_ai_quest_for_user(
                session=session,
                user=user,
                quest_type="weekly"
            )

            # Парсим задания
            tasks = json.loads(quest.tasks)
            tasks_text = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(tasks)])

            # Формируем сообщение
            difficulty_emoji = {
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "🔴")

            response = (
                f"🏆 **НОВЫЙ НЕДЕЛЬНЫЙ КВЕСТ** 🏆\n\n"
                f"{emoji} **{quest.title}**\n\n"
                f"📜 {quest.description}\n\n"
                f"📋 **Задания на неделю:**\n{tasks_text}\n\n"
                f"💪 Сложность: {quest.difficulty.upper()}\n\n"
                f"У тебя 7 дней чтобы доказать свою силу!\n"
                f"ID квеста: {quest.id}"
            )

            await message.answer(response, parse_mode="Markdown")

        except Exception as e:
            await message.answer(f"❌ Ошибка при генерации квеста: {e}")


@router.message(Command("my_quests"))
async def cmd_my_quests(message: Message):
    """
    Показывает активные квесты пользователя.
    """
    from database.crud import get_user_quests

    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        # Получаем активные квесты
        pending_quests = await get_user_quests(session, user.id, status="pending")

        if not pending_quests:
            await message.answer(
                "📭 У тебя пока нет активных квестов.\n\n"
                "Используй /generate_daily или /generate_weekly для создания квеста."
            )
            return

        response = "📋 **Твои активные квесты:**\n\n"

        for quest in pending_quests:
            difficulty_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "⚪")

            # Парсим задания
            tasks = json.loads(quest.tasks)
            tasks_text = "\n".join([f"    • {task}" for task in tasks])

            quest_type_text = "⚔️ ЕЖЕДНЕВНЫЙ" if quest.quest_type == "daily" else "🏆 НЕДЕЛЬНЫЙ"

            response += (
                f"{quest_type_text} {emoji}\n"
                f"**{quest.title}**\n"
                f"{quest.description}\n\n"
                f"**Задания:**\n{tasks_text}\n\n"
                f"ID: {quest.id}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(response, parse_mode="Markdown")
