from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date
from database import get_today_log, get_current_day

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# Клавиатура для запуска вечернего опроса
def evening_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать вечерний опрос 🌙", callback_data="evening_start")]
    ])

# Клавиатура для дневного напоминания
def afternoon_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😊 Хорошее", callback_data="mood_good")],
        [InlineKeyboardButton(text="😐 Нормальное", callback_data="mood_normal")],
        [InlineKeyboardButton(text="😫 Плохое", callback_data="mood_bad")],
        [InlineKeyboardButton(text="✏️ Изменить утренние ответы", callback_data="review_start")]
    ])

# Клавиатура для напоминания
def nag_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отметить сейчас 📝", callback_data="evening_start")]
    ])

async def morning_check(bot: Bot, user_id: int):
    await bot.send_message(user_id, "Доброе утро! Начинаем день?")

async def afternoon_check(bot: Bot, user_id: int):
    today = date.today()
    log = await get_today_log(user_id)
    
    text = "Не забудь пообедать нормальной едой! 🥗\n\nКак настроение?"
    
    if log and log.get('sweet_planned') == 'binge':
        text = "Помнишь, утром ты планировала сорваться? Держись 💪\n\n" + text
    
    await bot.send_message(user_id, text, reply_markup=afternoon_kb())

async def evening_check(bot: Bot, user_id: int):
    """22:00 — запускает полноценный вечерний опрос"""
    await bot.send_message(
        user_id, 
        "Как прошел день? Давай отметим сладкое и спорт 🌙",
        reply_markup=evening_start_kb()
    )

async def nag_user(bot: Bot, user_id: int):
    """23:30 — напоминание, если не ответила"""
    get_current_day()
    log = await get_today_log(user_id)
    
    # Проверяем, был ли вечерний опрос (есть ли sweet_bool)
    if not log or log.get('sweet_bool') is None:
        await bot.send_message(
            user_id,
            "Поля, ты забыла отметить день. Жду ответа 🥺",
            reply_markup=nag_kb()
        )

async def weekly_report(bot: Bot, user_id: int):
    """Вторник 9:00 — недельная сводка"""
    await bot.send_message(user_id, "Сегодня вторник — время недельной сводки! Напиши /stats 📊")

def setup_scheduler(bot: Bot, user_id: int):
    scheduler.add_job(morning_check, 'cron', hour=9, minute=0, args=[bot, user_id])
    scheduler.add_job(afternoon_check, 'cron', hour=14, minute=0, args=[bot, user_id])
    scheduler.add_job(evening_check, 'cron', hour=22, minute=00, args=[bot, user_id])
    scheduler.add_job(nag_user, 'cron', hour=23, minute=30, args=[bot, user_id])
    scheduler.add_job(weekly_report, 'cron', day_of_week='tue', hour=9, minute=0, args=[bot, user_id])
    scheduler.start()