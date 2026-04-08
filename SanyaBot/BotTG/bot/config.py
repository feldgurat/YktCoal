import os
from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")

# URL бэкенда (внутри docker-compose — имя сервиса)
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
=======
# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN в переменных окружения или .env файле")
>>>>>>> main
