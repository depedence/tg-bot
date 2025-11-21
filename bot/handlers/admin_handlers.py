from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.database import get_session
from services.admin_service import AdminService
from config.settings import ADMIN_IDS

router = Router()

@router.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message):
    """ Показать статистику (только для админов) """

    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав для просмотра статистики")
        return

    async for session in get_session():
        stats = await AdminService.get_statistics(session)

        text = (
            "📊 <b>Статистика бота</b>\n\n"
            f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
            f"✅ Выполнено квестов: <b>{stats['completed_quests']}</b>\n"
            f"⭐ Средний уровень: <b>{stats['avg_level']}</b>\n"
        )

        await message.answer(text, parse_mode="HTML")