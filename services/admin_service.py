from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Quest

class AdminService:
    @staticmethod
    async def get_statistics(session: AsyncSession) -> dict:
        """Получить статистику для администратора"""

        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()

        result = await session.execute(
            select(func.count(Quest.id)).where(Quest.status == 'completed')
        )
        completed_quests = result.scalar()

        result = await session.execute(select(func.avg(User.level)))
        avg_level = result.scalar()
        avg_level = round(avg_level, 1) if avg_level else 0

        return {
            'total_users': total_users or 0,
            'completed_quests': completed_quests or 0,
            'avg_level': avg_level
        }