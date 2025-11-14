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
from sqlalchemy import select
from database.models import Quest
from utils.logger import logger
import json


router = Router()


@router.message(F.text == "⚔️ Дейли квест")
@router.message(Command("generate_daily"))
async def cmd_generate_daily(message: Message):
    """
    Генерирует дейли квест вручную.
    """
    logger.info(
        'Запрос генерации дейли квеста',
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    try:

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
                logger.exception(
                    'Ошибка при генерации дейли квеста',
                    user_id=message.from_user.id
                )
                await loading_msg.delete()
                await message.answer(f"❌ Ошибка при генерации квеста:\n{e}")

    except Exception as e:
        logger.exception(
            'Критическая ошибка в cmd_generate_daily',
            user_id=message.from_user.id
        )
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "🏆 Недельный квест")
@router.message(Command("generate_weekly"))
async def cmd_generate_weekly(message: Message):
    """
    Генерирует недельный квест вручную.
    """
    logger.info(
        'Запрос генерации недельного квеста',
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    try:

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
                logger.exception(
                    'Ошибка при генерации недельного квеста',
                    user_id=message.from_user.id
                )
                await loading_msg.delete()
                await message.answer(f"❌ Ошибка при генерации квеста:\n{e}")

    except Exception as e:
        logger.exception(
            'Критическая ошибка в cmd_generate_weekly',
            user_id=message.from_user.id
        )
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "📋 Мои квесты")
@router.message(Command("my_quests"))
async def cmd_my_quests(message: Message):
    """
    Показывает активные квесты пользователя с кнопками для отметки заданий.
    """
    from bot.keyboards.inline import get_quest_keyboard

    logger.info(
        'Запрос на все квесты пользователя',
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    try:

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

    except Exception as e:
        logger.exception(
            'Критическая ошибка в cmd_my_quests',
            user_id=message.from_user.id
        )
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Показывает статистику пользователя.
    """
    from services.level_service import get_level_from_experience

    logger.info(
        'Запрос на статистику пользователя',
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    try:

        async with async_session_maker() as session:
            user = await get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )

            # Получаем все квесты
            all_quests = await get_user_quests(session, user.id)
            completed = [q for q in all_quests if q.status == "completed"]
            failed = [q for q in all_quests if q.status == "failed"]
            pending = [q for q in all_quests if q.status == "pending"]

            # Информация об уровне
            current_level, current_exp, exp_needed = get_level_from_experience(user.experience)

            # Формируем никнейм
            if user.username:
                nickname = f"@{user.username}"
            else:
                nickname = user.first_name

            response = (
                f"👤 {nickname}\n\n"
                f"⭐ Уровень: {current_level}\n"
                f"⚡ Опыт: {current_exp}/{exp_needed}\n\n"
                f"📊 СТАТИСТИКА КВЕСТОВ:\n\n"
                f"✅ Выполнено: {len(completed)}\n"
                f"❌ Провалено: {len(failed)}\n"
                f"⏳ Активных: {len(pending)}\n"
                f"📈 Всего квестов: {len(all_quests)}\n"
            )

            if len(all_quests) > 0:
                success_rate = (len(completed) / len(all_quests)) * 100
                response += f"🎯 Процент успеха: {success_rate:.1f}%\n\n"

            response += (
                f"💪 Выполняйте больше квестов,\n"
                f"чтобы поднять свой уровень!"
            )

            await message.answer(response)

    except Exception as e:
        logger.exception(
            'Критическая ошибка в cmd_stats',
            user_id=message.from_user.id
        )
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("toggle_task:"))
async def callback_toggle_task(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку отметки задания.
    """
    try:
        _, quest_id, task_index = callback.data.split(":")
        quest_id = int(quest_id)
        task_index = int(task_index)

        async with async_session_maker() as session:
            # Получаем квест ДО изменения
            result = await session.execute(
                select(Quest).where(Quest.id == quest_id)
            )
            quest_before = result.scalar_one()
            completed_before = json.loads(quest_before.completed_tasks)

            # Проверяем: пытается ли пользователь снять отметку с выполненного задания
            if task_index in completed_before:
                await callback.answer(
                    "⚠️ Задание уже выполнено!\n"
                    "Если ты нажал случайно - выполни задание по-настоящему.",
                    show_alert=True
                )
                return

            # Получаем пользователя
            user = await get_or_create_user(
                session=session,
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name
            )

            # Переключаем статус задания
            quest = await toggle_task_completion(session, quest_id, task_index)

            tasks = json.loads(quest.tasks)
            completed_tasks_list = json.loads(quest.completed_tasks)

            # НАЧИСЛЕНИЕ ОПЫТА (только при отметке как выполненное)
            exp_message = ""
            if task_index in completed_tasks_list:  # Задание отмечено как выполненное
                from services.level_service import get_level_from_experience
                from database.crud import add_experience

                # Считаем опыт за это задание
                if quest.quest_type == "daily":
                    task_exp = 1
                else:
                    task_exp = 3

                # Проверяем все ли задания выполнены
                all_completed = len(completed_tasks_list) == len(tasks)
                bonus_exp = 0

                if all_completed:
                    if quest.quest_type == "daily":
                        bonus_exp = 1
                    else:
                        bonus_exp = 3

                total_exp = task_exp + bonus_exp

                # Начисляем опыт
                user, level_up, new_level = await add_experience(session, user.id, total_exp)

                # Формируем сообщение о получении опыта
                if all_completed:
                    exp_message = f"\n\n🎉 КВЕСТ ПОЛНОСТЬЮ ВЫПОЛНЕН!\n"
                    exp_message += f"💫 +{task_exp} опыта за задание\n"
                    exp_message += f"⭐ +{bonus_exp} бонусный опыт за завершение квеста!\n"
                else:
                    exp_message += f"\n\n✅ Задание выполнено!\n"
                    exp_message += f"💫 +{task_exp} опыта\n"

                # Информация об уровне
                current_level, current_exp, exp_needed = get_level_from_experience(user.experience)
                exp_message += f"\n📊 Уровень: {current_level}\n"
                exp_message += f"⚡ Опыт: {current_exp}/{exp_needed}"

                # Если был levelup
                if level_up:
                    exp_message += f"\n\n🎊 ПОЗДРАВЛЯЕМ! 🎊\n"
                    exp_message += f"🆙 Вы достигли {new_level} уровня!"

            # Формируем текст квеста
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

            response = f"{quest_icon} {quest_type_name} {emoji}\n"
            response += f"{quest.title}\n\n"
            response += f"{quest.description}\n\n"
            response += "Задания:\n"

            for i, task in enumerate(tasks):
                status = "✅" if i in completed_tasks_list else "⬜"
                response += f"{i+1}. {status} {task}\n"

            progress = f"{len(completed_tasks_list)}/{len(tasks)}"
            response += f"\n📊 Прогресс: {progress}"

            if quest.status == "completed":
                response += f"\n\n🏆 КВЕСТ ЗАВЕРШЕН!"
            else:
                response += f"\n⏰ Сгорит через: {hours_left}ч {minutes_left}мин"

            # Обновляем сообщение
            await callback.message.edit_text(
                response,
                reply_markup=get_quest_keyboard(quest.id, tasks, completed_tasks_list)
            )

            # Отправляем уведомление об опыте отдельным сообщением
            if exp_message:
                await callback.message.answer(exp_message)
                await callback.answer("✅ Отлично!")
            else:
                await callback.answer("⬜ Отметка снята")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
