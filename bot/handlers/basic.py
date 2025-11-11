"""
Обработчики базовых команд бота.
"""
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from database.database import async_session_maker
from database.crud import get_or_create_user, save_message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Регистрирует пользователя в БД и приветствует.
    """
    async with async_session_maker() as session:
        # Регистрируем/получаем пользователя
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        # Сохраняем сообщение пользователя в историю
        await save_message(
            session=session,
            user_id=user.id,
            message_text=message.text,
            is_from_user=True
        )

        response_text = (
            f"Привет, {message.from_user.first_name}!\n\n"
            f"Я RPG Quest Bot - твой личный квестодатель.\n"
            f"Используй /help чтобы узнать что я умею."
        )

        await message.answer(response_text)

        # Сохраняем ответ бота в историю
        await save_message(
            session=session,
            user_id=user.id,
            message_text=response_text,
            is_from_user=False
        )


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
            "📋 Доступные команды:\n\n"
            "🏠 Основные:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n\n"
            "⚔️ Квесты:\n"
            "/my_quests - Мои активные квесты\n"
            "/generate_daily - Создать дейли квест (тест)\n"
            "/generate_weekly - Создать недельный квест (тест)\n\n"
            "🤖 Автоматика:\n"
            "Бот автоматически создает квесты:\n"
            "  • Ежедневные: каждый день в 9:00\n"
            "  • Недельные: каждый понедельник в 9:00\n\n"
            "💪 Доказывай Системе свою силу!"
        )

        await message.answer(response_text)
        await save_message(session, user.id, response_text, False)
