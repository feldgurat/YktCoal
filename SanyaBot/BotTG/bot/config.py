import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")

# URL бэкенда (внутри docker-compose — имя сервиса)
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
