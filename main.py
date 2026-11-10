import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, USER_ID
from database import init_db, migrate_db, init_schedule_db
from handlers import router
from init_protocol import init_protocol
from scheduler import setup_scheduler

async def main():
    await init_db()
    await migrate_db()  # <-- ДОБАВИТЬ
    await init_schedule_db()
    await init_protocol()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    setup_scheduler(bot, USER_ID)
    
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())