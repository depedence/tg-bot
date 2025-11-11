import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')

if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не найден в .env файле')

if not API_KEY:
    raise ValueError('API_KEY не найден в .env файле')
