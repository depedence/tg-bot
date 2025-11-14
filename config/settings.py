import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
# API_KEY = os.getenv('API_KEY')

# Database
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql')
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "quest_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не найден в .env файле')

# if not API_KEY:
#     raise ValueError('API_KEY не найден в .env файле')

def get_database_url() -> str:
    if DATABASE_TYPE == 'postgresql':
        return f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        return "sqlite+aiosqlite:///./quest_bot.db"
