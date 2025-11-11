"""
Функции для работы с базой данных.
"""
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Quest, ChatHistory
from datetime import datetime
from typing import Optional
from services.ai_service import generate_daily_quest, generate_weekly_quest


# ========== USERS ==========

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: str
) -> User:
    """
    Получает пользователя из БД или создает нового если не существует.
    """
    # Ищем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    # Если не нашли - создаем
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"✅ Создан новый пользователь: {telegram_id}")

    return user


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """
    Получает пользователя по telegram_id.
    """
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


# ========== QUESTS ==========

async def create_quest(
    session: AsyncSession,
    user_id: int,
    title: str,
    description: str,
    tasks: list[str],  # Теперь принимаем список заданий
    difficulty: str,
    quest_type: str
) -> Quest:
    """
    Создает новый квест для пользователя.
    """
    quest = Quest(
        user_id=user_id,
        title=title,
        description=description,
        tasks=json.dumps(tasks, ensure_ascii=False),  # Сохраняем как JSON строку
        difficulty=difficulty,
        quest_type=quest_type,
        status="pending"
    )
    session.add(quest)
    await session.commit()
    await session.refresh(quest)
    return quest


async def get_user_quests(
    session: AsyncSession,
    user_id: int,
    status: Optional[str] = None
) -> list[Quest]:
    """
    Получает квесты пользователя.
    Можно фильтровать по статусу (pending/completed/failed).
    """
    query = select(Quest).where(Quest.user_id == user_id)

    if status:
        query = query.where(Quest.status == status)

    result = await session.execute(query.order_by(Quest.created_at.desc()))
    return list(result.scalars().all())


async def complete_quest(
    session: AsyncSession,
    quest_id: int
) -> Quest:
    """
    Отмечает квест как выполненный.
    """
    result = await session.execute(
        select(Quest).where(Quest.id == quest_id)
    )
    quest = result.scalar_one()

    quest.status = "completed"
    quest.completed_at = datetime.utcnow()

    await session.commit()
    await session.refresh(quest)
    return quest


async def fail_quest(
    session: AsyncSession,
    quest_id: int
) -> Quest:
    """
    Отмечает квест как проваленный.
    """
    result = await session.execute(
        select(Quest).where(Quest.id == quest_id)
    )
    quest = result.scalar_one()

    quest.status = "failed"

    await session.commit()
    await session.refresh(quest)
    return quest


# ========== CHAT HISTORY ==========

async def save_message(
    session: AsyncSession,
    user_id: int,
    message_text: str,
    is_from_user: bool
):
    """
    Сохраняет сообщение в историю чата.
    """
    chat_entry = ChatHistory(
        user_id=user_id,
        message_text=message_text,
        is_from_user=is_from_user
    )
    session.add(chat_entry)
    await session.commit()


async def get_user_chat_history(
    session: AsyncSession,
    user_id: int,
    limit: int = 50
) -> list[ChatHistory]:
    """
    Получает историю чата пользователя.
    По умолчанию последние 50 сообщений.
    """
    result = await session.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))  # Переворачиваем чтобы старые были сначала

async def create_ai_quest_for_user(
    session: AsyncSession,
    user: User,
    quest_type: str  # "daily" или "weekly"
) -> Quest:
    """
    Генерирует квест через AI и сохраняет в БД.

    Args:
        session: Сессия БД
        user: Пользователь для которого генерируем квест
        quest_type: Тип квеста ("daily" или "weekly")

    Returns:
        Созданный квест
    """
    # Генерируем квест через AI
    if quest_type == "daily":
        quest_data = generate_daily_quest(user_name=user.first_name)
    else:
        quest_data = generate_weekly_quest(user_name=user.first_name)

    # Создаем квест в БД
    quest = await create_quest(
        session=session,
        user_id=user.id,
        title=quest_data["title"],
        description=quest_data["description"],
        tasks=quest_data["tasks"],
        difficulty=quest_data["difficulty"],
        quest_type=quest_type
    )

    return quest

async def get_active_quest_by_type(
    session: AsyncSession,
    user_id: int,
    quest_type: str
) -> Optional[Quest]:
    """
    Получает активный квест определенного типа (daily/weekly).
    Возвращает None если активного квеста нет.
    """
    result = await session.execute(
        select(Quest)
        .where(Quest.user_id == user_id)
        .where(Quest.quest_type == quest_type)
        .where(Quest.status == "pending")
        .order_by(Quest.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def check_can_generate_quest(
    session: AsyncSession,
    user_id: int,
    quest_type: str
) -> tuple[bool, str]:
    """
    Проверяет может ли пользователь получить новый квест.

    Returns:
        tuple[bool, str]: (можно ли создать квест, сообщение для пользователя)
    """
    active_quest = await get_active_quest_by_type(session, user_id, quest_type)

    if not active_quest:
        return True, ""

    # Рассчитываем когда квест сгорит
    from datetime import timedelta

    if quest_type == "daily":
        expires_at = active_quest.created_at + timedelta(hours=24)
        quest_name = "ежедневный квест"
    else:
        expires_at = active_quest.created_at + timedelta(days=7)
        quest_name = "недельный квест"

    # Форматируем время
    time_left = expires_at - datetime.utcnow()

    if time_left.total_seconds() <= 0:
        # Квест истек - можно создавать новый
        return True, ""

    # Квест еще активен
    hours_left = int(time_left.total_seconds() // 3600)
    minutes_left = int((time_left.total_seconds() % 3600) // 60)

    message = (
        f"⏳ У тебя уже есть активный {quest_name}!\n\n"
        f"Новый квест будет доступен через: {hours_left}ч {minutes_left}мин\n\n"
        f"Используй /my_quests чтобы увидеть текущие квесты."
    )

    return False, message
