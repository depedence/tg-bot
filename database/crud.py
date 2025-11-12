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
from services.level_service import get_level_from_experience
from datetime import timedelta


# ========== USERS ==========

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: str
) -> User:

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

    quest = Quest(
        user_id=user_id,
        title=title,
        description=description,
        tasks=json.dumps(tasks, ensure_ascii=False),  # Сохраняем как JSON строку
        completed_tasks='[]',
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

    query = select(Quest).where(Quest.user_id == user_id)

    if status:
        query = query.where(Quest.status == status)

    result = await session.execute(query.order_by(Quest.created_at.desc()))
    return list(result.scalars().all())


async def complete_quest(
    session: AsyncSession,
    quest_id: int
) -> Quest:

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

    # Определяем период проверки
    if quest_type == "daily":
        time_period = timedelta(hours=24)
        quest_name = "ежедневный квест"
    else:
        time_period = timedelta(days=7)
        quest_name = "недельный квест"

    # Ищем ЛЮБЫЕ квесты этого типа за период (и активные, и выполненные)
    cutoff_time = datetime.utcnow() - time_period

    result = await session.execute(
        select(Quest)
        .where(Quest.user_id == user_id)
        .where(Quest.quest_type == quest_type)
        .where(Quest.created_at >= cutoff_time)
        .order_by(Quest.created_at.desc())
        .limit(1)
    )
    last_quest = result.scalar_one_or_none()

    if not last_quest:
        # Квестов за этот период нет - можно создавать
        return True, ""

    # Рассчитываем когда можно будет взять новый квест
    next_available = last_quest.created_at + time_period
    time_left = next_available - datetime.utcnow()

    if time_left.total_seconds() <= 0:
        # Время прошло - можно создавать
        return True, ""

    # Квест еще нельзя взять
    hours_left = int(time_left.total_seconds() // 3600)
    minutes_left = int((time_left.total_seconds() % 3600) // 60)

    message = (
        f"⏳ Ты уже брал {quest_name} недавно!\n\n"
        f"Новый квест будет доступен через:\n"
        f"🕐 {hours_left}ч {minutes_left}мин\n\n"
        f"⚔️ Один {quest_name} в "
        f"{'сутки' if quest_type == 'daily' else '7 дней'}!"
    )

    return False, message

async def toggle_task_completion(
    session: AsyncSession,
    quest_id: int,
    task_index: int
) -> Quest:

    result = await session.execute(
        select(Quest).where(Quest.id == quest_id)
    )
    quest = result.scalar_one()

    # Парсим список выполненных заданий
    completed = json.loads(quest.completed_tasks)

    # Переключаем статус
    if task_index in completed:
        completed.remove(task_index)  # Убираем из выполненных
    else:
        completed.append(task_index)  # Добавляем в выполненные

    # Сохраняем обратно
    quest.completed_tasks = json.dumps(completed)

    # Проверяем все ли задания выполнены
    tasks = json.loads(quest.tasks)
    if len(completed) == len(tasks):
        quest.status = "completed"
        quest.completed_at = datetime.utcnow()
    else:
        quest.status = "pending"
        quest.completed_at = None

    await session.commit()
    await session.refresh(quest)

    return quest

async def add_experience(
    session: AsyncSession,
    user_id: int,
    exp_amount: int
) -> tuple[User, bool, int]:

    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one()

    old_level = user.level
    user.experience += exp_amount

    # Вычисляем новый уровень
    new_level, _, _ = get_level_from_experience(user.experience)

    level_up = new_level > old_level
    user.level = new_level

    await session.commit()
    await session.refresh(user)

    return user, level_up, new_level
