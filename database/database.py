from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from database.models import Base  # ← импортируй Base из models
from config.settings import get_database_url, DATABASE_TYPE
import logging

logger = logging.getLogger(__name__)

# class Base(DeclarativeBase):
#     pass

database_url = get_database_url()

# Создаём engine с учётом типа базы
if DATABASE_TYPE == "sqlite":
    engine: AsyncEngine = create_async_engine(
        database_url,
        echo=False
    )
else:  # PostgreSQL
    engine: AsyncEngine = create_async_engine(
        database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ База данных инициализирована (тип: {DATABASE_TYPE})")

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
