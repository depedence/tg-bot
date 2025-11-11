"""
Reply клавиатуры для бота.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Главное меню бота с основными командами.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Мои квесты"),
                KeyboardButton(text="📊 Статистика")
            ],
            [
                KeyboardButton(text="⚔️ Дейли квест"),
                KeyboardButton(text="🏆 Недельный квест")
            ],
            [
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,  # Подстраивает размер кнопок
        input_field_placeholder="Выбери команду из меню"
    )
    return keyboard
