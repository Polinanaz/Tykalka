from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from scheduler import setup_scheduler
from database import init_db, migrate_db, init_schedule_db
from config import BOT_TOKEN, USER_ID
import asyncio

async def main():
    await init_db()
    await migrate_db()
    await init_schedule_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    # ЗАПУСКАЕМ SCHEDULER
    setup_scheduler(bot, USER_ID)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())