"""
Обработчики базовых команд бота.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from database.database import async_session_maker
from database.crud import get_or_create_user, save_message
from bot.keyboards.reply import get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Регистрирует пользователя в БД и приветствует.
    """
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        await save_message(
            session=session,
            user_id=user.id,
            message_text=message.text,
            is_from_user=True
        )

        response_text = (
            f"👋 Приветствую, {message.from_user.first_name}!\n\n"
            "⚔️ Я СИСТЕМА ПРОКАЧКИ\n\n"
            "Я буду выдавать тебе квесты для саморазвития. "
            "Твоя задача — выполнять их и становиться лучше с каждым днем.\n\n"
            "Система не прощает слабости.\n"
            "Только упорство ведет к победе.\n\n"
            "Используй /help чтобы узнать команды."
        )

        await message.answer(response_text, reply_markup=get_main_menu())

        await save_message(
            session=session,
            user_id=user.id,
            message_text=response_text,
            is_from_user=False
        )


@router.message(F.text == "❓ Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help.
    """
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        await save_message(session, user.id, message.text, True)

        response_text = (
            "📋 ДОСТУПНЫЕ КОМАНДЫ\n\n"
            "🏠 Основные:\n"
            "/start — Перезапустить бота\n"
            "/help — Показать команды\n\n"
            "⚔️ Квесты:\n"
            "/my_quests — Мои активные квесты\n"
            "/generate_daily — Получить дейли\n"
            "/generate_weekly — Получить недельный\n\n"
            "🤖 Автоматическая выдача:\n"
            "• Дейли: каждый день в 9:00\n"
            "• Недельные: каждый понедельник в 9:00\n\n"
            "💪 Доказывай Системе свою силу!"
        )

        await message.answer(response_text)
        await save_message(session, user.id, response_text, False)
