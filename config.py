import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env из текущей директории
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

# Проверка
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверь файл .env")
if not USER_ID:
    raise ValueError("USER_ID не найден! Проверь файл .env")

USER_ID = int(USER_ID)
TIMEZONE = "Europe/Moscow"