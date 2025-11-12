"""
Административные команды для тестирования.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from database.database import async_session_maker
from database.crud import (get_or_create_user, create_ai_quest_for_user, check_can_generate_quest, get_user_quests, toggle_task_completion)
from bot.keyboards.inline import get_quest_keyboard
from datetime import datetime, timedelta
import json

router = Router()


@router.message(F.text == "⚔️ Дейли квест")
@router.message(Command("generate_daily"))
async def cmd_generate_daily(message: Message):
    """
    Генерирует дейли квест вручную.
    """
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        can_generate, error_message = await check_can_generate_quest(
            session, user.id, "daily"
        )

        if not can_generate:
            await message.answer(error_message)
            return

        loading_msg = await message.answer("⏳ Генерирую ежедневный квест...")

        try:
            quest = await create_ai_quest_for_user(
                session=session,
                user=user,
                quest_type="daily"
            )

            tasks = json.loads(quest.tasks)

            difficulty_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "⚪")

            response = f"⚔️ НОВЫЙ ЕЖЕДНЕВНЫЙ КВЕСТ\n\n"
            response += f"{emoji} {quest.title}\n\n"
            response += f"{quest.description}\n\n"
            response += "📋 ЗАДАНИЯ:\n"

            for i, task in enumerate(tasks, 1):
                response += f"{i}. {task}\n"

            response += f"\n💪 Сложность: {quest.difficulty.upper()}"
            response += f"\n⏰ Время: 24 часа"

            await loading_msg.delete()

            # Отправляем с кнопками
            from bot.keyboards.inline import get_quest_keyboard
            tasks_list = json.loads(quest.tasks)
            await message.answer(
                response,
                reply_markup=get_quest_keyboard(quest.id, tasks_list, [])
            )

        except Exception as e:
            await loading_msg.delete()
            await message.answer(f"❌ Ошибка при генерации квеста:\n{e}")


@router.message(F.text == "🏆 Недельный квест")
@router.message(Command("generate_weekly"))
async def cmd_generate_weekly(message: Message):
    """
    Генерирует недельный квест вручную.
    """
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        can_generate, error_message = await check_can_generate_quest(
            session, user.id, "weekly"
        )

        if not can_generate:
            await message.answer(error_message)
            return

        loading_msg = await message.answer("⏳ Генерирую недельный квест...")

        try:
            quest = await create_ai_quest_for_user(
                session=session,
                user=user,
                quest_type="weekly"
            )

            tasks = json.loads(quest.tasks)

            difficulty_emoji = {
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "🔴")

            response = f"🏆 НОВЫЙ НЕДЕЛЬНЫЙ КВЕСТ\n\n"
            response += f"{emoji} {quest.title}\n\n"
            response += f"{quest.description}\n\n"
            response += "📋 ЗАДАНИЯ НА НЕДЕЛЮ:\n"

            for i, task in enumerate(tasks, 1):
                response += f"{i}. {task}\n"

            response += f"\n💪 Сложность: {quest.difficulty.upper()}"
            response += f"\n⏰ Время: 7 дней"

            await loading_msg.delete()

            # Отправляем с кнопками
            from bot.keyboards.inline import get_quest_keyboard
            tasks_list = json.loads(quest.tasks)
            await message.answer(
                response,
                reply_markup=get_quest_keyboard(quest.id, tasks_list, [])
            )

        except Exception as e:
            await loading_msg.delete()
            await message.answer(f"❌ Ошибка при генерации квеста:\n{e}")


@router.message(F.text == "📋 Мои квесты")
@router.message(Command("my_quests"))
async def cmd_my_quests(message: Message):
    """
    Показывает активные квесты пользователя с кнопками для отметки заданий.
    """
    from bot.keyboards.inline import get_quest_keyboard

    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        pending_quests = await get_user_quests(session, user.id, status="pending")

        if not pending_quests:
            await message.answer(
                "📭 У тебя пока нет активных квестов.\n\n"
                "Создай квест используя кнопки меню:"
            )
            return

        # Отправляем каждый квест отдельным сообщением с кнопками
        for quest in pending_quests:
            difficulty_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "⚪")

            tasks = json.loads(quest.tasks)
            completed_tasks = json.loads(quest.completed_tasks)

            if quest.quest_type == "daily":
                expires_at = quest.created_at + timedelta(hours=24)
                quest_icon = "⚔️"
                quest_type_name = "ЕЖЕДНЕВНЫЙ"
            else:
                expires_at = quest.created_at + timedelta(days=7)
                quest_icon = "🏆"
                quest_type_name = "НЕДЕЛЬНЫЙ"

            time_left = expires_at - datetime.utcnow()
            hours_left = int(time_left.total_seconds() // 3600)
            minutes_left = int((time_left.total_seconds() % 3600) // 60)

            # Формируем текст с отметками выполнения
            response = f"{quest_icon} {quest_type_name} {emoji}\n"
            response += f"{quest.title}\n\n"
            response += f"{quest.description}\n\n"
            response += "Задания:\n"

            for i, task in enumerate(tasks):
                status = "✅" if i in completed_tasks else "⬜"
                response += f"{i+1}. {status} {task}\n"

            # Прогресс
            progress = f"{len(completed_tasks)}/{len(tasks)}"
            response += f"\n📊 Прогресс: {progress}"
            response += f"\n⏰ Сгорит через: {hours_left}ч {minutes_left}мин"

            # Отправляем с кнопками
            await message.answer(
                response,
                reply_markup=get_quest_keyboard(quest.id, tasks, completed_tasks)
            )


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Показывает статистику пользователя.
    """
    await message.answer(
        "📊 СТАТИСТИКА\n\n"
        "🚧 Эта функция в разработке.\n"
        "Скоро здесь появится твой прогресс!"
    )

@router.callback_query(F.data.startswith("toggle_task:"))
async def callback_toggle_task(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку отметки задания.
    Формат callback_data: "toggle_task:quest_id:task_index"
    """
    try:
        # Парсим данные из callback
        _, quest_id, task_index = callback.data.split(":")
        quest_id = int(quest_id)
        task_index = int(task_index)

        async with async_session_maker() as session:
            # Переключаем статус задания
            quest = await toggle_task_completion(session, quest_id, task_index)

            tasks = json.loads(quest.tasks)
            completed_tasks = json.loads(quest.completed_tasks)

            difficulty_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(quest.difficulty, "⚪")

            if quest.quest_type == "daily":
                expires_at = quest.created_at + timedelta(hours=24)
                quest_icon = "⚔️"
                quest_type_name = "ЕЖЕДНЕВНЫЙ"
            else:
                expires_at = quest.created_at + timedelta(days=7)
                quest_icon = "🏆"
                quest_type_name = "НЕДЕЛЬНЫЙ"

            time_left = expires_at - datetime.utcnow()
            hours_left = int(time_left.total_seconds() // 3600)
            minutes_left = int((time_left.total_seconds() % 3600) // 60)

            # Обновляем текст сообщения
            response = f"{quest_icon} {quest_type_name} {emoji}\n"
            response += f"{quest.title}\n\n"
            response += f"{quest.description}\n\n"
            response += "Задания:\n"

            for i, task in enumerate(tasks):
                status = "✅" if i in completed_tasks else "⬜"
                response += f"{i+1}. {status} {task}\n"

            progress = f"{len(completed_tasks)}/{len(tasks)}"
            response += f"\n📊 Прогресс: {progress}"

            # Если все задания выполнены - поздравляем
            if quest.status == "completed":
                response += f"\n\n🎉 КВЕСТ ВЫПОЛНЕН! 🎉\n💪 Отличная работа!"
            else:
                response += f"\n⏰ Сгорит через: {hours_left}ч {minutes_left}мин"

            # Обновляем сообщение с новыми кнопками
            await callback.message.edit_text(
                response,
                reply_markup=get_quest_keyboard(quest.id, tasks, completed_tasks)
            )

            # Уведомляем пользователя
            if task_index in completed_tasks:
                await callback.answer("✅ Задание отмечено как выполненное!")
            else:
                await callback.answer("⬜ Отметка снята")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
