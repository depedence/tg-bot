"""
Inline клавиатуры для квестов.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json


def get_quest_keyboard(quest_id: int, tasks: list[str], completed_tasks: list[int]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для отметки заданий.

    Args:
        quest_id: ID квеста
        tasks: Список заданий
        completed_tasks: Список индексов выполненных заданий
    """
    buttons = []

    for idx, task in enumerate(tasks):
        # Если задание выполнено - галочка, иначе - пустой квадрат
        status = "✅" if idx in completed_tasks else "⬜"
        button_text = f"{status} Задание {idx + 1}"

        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"toggle_task:{quest_id}:{idx}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
