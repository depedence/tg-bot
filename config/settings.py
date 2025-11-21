import os
from dotenv import load_dotenv
from pathlib import Path

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

if ENVIRONMENT == "prod":
    env_file = Path('.env.prod')
else:
    env_file = Path('.env.dev')

if not env_file.exists():
    raise FileNotFoundError(f"Файл конфигурации {env_file} не найден!")

load_dotenv(env_file)

print(f"🔧 Окружение: {ENVIRONMENT}")
print(f"🔧 Конфиг: {env_file}")

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
API_KEY = os.getenv("API_KEY")

# Database
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Yandex Cloud
YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")

# Quest settings
QUEST_DAILY_HOURS = float(os.getenv("QUEST_DAILY_HOURS", "24"))
QUEST_WEEKLY_HOURS = float(os.getenv("QUEST_WEEKLY_HOURS", "168"))
SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "60"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")
if not DB_NAME:
    raise ValueError("DB_NAME не установлен!")

print(f"✅ Настройки загружены для окружения: {ENVIRONMENT}")


def get_database_url() -> str:
    """
    Формирует строку подключения к базе данных.
    """
    if DATABASE_TYPE == "sqlite":
        return f"sqlite+aiosqlite:///{DB_NAME}"
    elif DATABASE_TYPE == "postgresql":
        return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError(f"Неподдерживаемый тип базы данных: {DATABASE_TYPE}")
