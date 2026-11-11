from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, datetime, timedelta
from database import get_today_log, get_current_day, parse_workout_time

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# === КЛАВИАТУРЫ ===

def morning_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать утренний опрос ☀️", callback_data="morning_start")]
    ])

def evening_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать вечерний опрос 🌙", callback_data="evening_start")]
    ])

def afternoon_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😊 Хорошее", callback_data="mood_good")],
        [InlineKeyboardButton(text="😐 Нормальное", callback_data="mood_normal")],
        [InlineKeyboardButton(text="😫 Плохое", callback_data="mood_bad")],
        [InlineKeyboardButton(text="✏️ Изменить утренние ответы", callback_data="review_start")]
    ])

def nag_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отметить сейчас 📝", callback_data="evening_start")]
    ])

# === ДЖОБЫ ===

async def morning_check(bot: Bot, user_id: int):
    """9:00 — запускает полноценный утренний опрос"""
    await bot.send_message(
        user_id,
        "Доброе утро! Как спалось? Давай заполним дневник ☀️",
        reply_markup=morning_start_kb()
    )

async def afternoon_check(bot: Bot, user_id: int):
    """14:00 — дневное напоминание"""
    log = await get_today_log(user_id)
    text = "Не забудь пообедать нормальной едой! 🥗\n\n"
    
    if log and log.get('daily_plan'):
        text += f"📝 Твой план на день:\n{log['daily_plan']}\n\n"
    
    text += "Как настроение?"
    
    if log and log.get('sweet_planned') == 'binge':
        text = "Помнишь, утром ты планировала сорваться? Держись 💪\n\n" + text
    
    await bot.send_message(user_id, text, reply_markup=afternoon_kb())

async def evening_check(bot: Bot, user_id: int):
    """22:00 — вечерний опрос"""
    await bot.send_message(
        user_id,
        "Как прошел день? Давай отметим сладкое и спорт 🌙",
        reply_markup=evening_start_kb()
    )

async def nag_user(bot: Bot, user_id: int):
    """23:30 — напоминание, если не ответила"""
    log = await get_today_log(user_id)
    if not log or log.get('sweet_bool') is None:
        await bot.send_message(
            user_id,
            "Поля, ты забыла отметить день. Жду ответа 🥺",
            reply_markup=nag_kb()
        )

async def weekly_report(bot: Bot, user_id: int):
    """Вторник 9:00 — недельная сводка"""
    await bot.send_message(user_id, "Сегодня вторник — время недельной сводки! Напиши /stats 📊")

async def workout_reminder(bot: Bot, user_id: int):
    """Напоминание за час до тренировки. Запускается каждые 15 минут."""
    log = await get_today_log(user_id)
    if not log or not log.get('workout_time'):
        return

    workout_dt = parse_workout_time(log['workout_time'])
    if not workout_dt:
        return

    now = datetime.now()
    time_until_workout = workout_dt - now

    if timedelta(minutes=55) <= time_until_workout <= timedelta(minutes=65):
        daily_plan = log.get('daily_plan', '')
        workout_plan = log.get('workout_plan', '')
        sport_planned = log.get('sport_planned', '')
        
        text = f"⏰ Через час у тебя тренировка ({log['workout_time']})!\n\n"
        
        if workout_plan:
            text += f"🏋️ План на тренировку:\n{workout_plan}\n\n"
        
        if daily_plan:
            text += f"📝 План на день:\n{daily_plan}\n\n"
        
        if sport_planned == 'lazy':
            text += "💪 Помнишь, утром было лень? Сейчас самое время собраться!"
        elif sport_planned == 'yes':
            text += "💪 Ты планировала пойти. Удачи!"
        
        await bot.send_message(user_id, text)

# === РАСПИСАНИЕ (ТАБЛЕТКИ/ПЛАН) ===

DB_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

async def schedule_morning_reminder(bot: Bot, user_id: int):
    await send_schedule_message(bot, user_id, "morning", "Доброе утро! ☀️ Вот твой протокол на сегодня:")

async def schedule_day_reminder(bot: Bot, user_id: int):
    await send_schedule_message(bot, user_id, "day", "Напоминание на день 🌤")

async def schedule_evening_reminder(bot: Bot, user_id: int):
    await send_schedule_message(bot, user_id, "evening", "Вечерний чек-лист 🌙")

async def send_schedule_message(bot: Bot, user_id: int, time_of_day: str, header: str):
    from database import get_user_schedule
    
    schedule = await get_user_schedule(user_id)
    today_en = DB_DAYS[datetime.now().weekday()]
    
    day_schedule = schedule.get(today_en, "")
    if not day_schedule:
        return
        
    parts = day_schedule.split("🌙 Вечер:")
    evening_part = parts[1].strip() if len(parts) > 1 else ""
    
    parts = parts[0].split("🌤 День:")
    day_part = parts[1].strip() if len(parts) > 1 else ""
    morning_part = parts[0].replace("☀️ Утро:", "").strip()
    
    target_text = ""
    if time_of_day == "morning":
        target_text = morning_part
    elif time_of_day == "day":
        target_text = day_part
    elif time_of_day == "evening":
        target_text = evening_part
        
    if target_text and target_text != "Не требуется":
        await bot.send_message(user_id, f"{header}\n\n{target_text}")

# === ОДНА ФУНКЦИЯ НАСТРОЙКИ (ОБЪЕДИНЁННАЯ) ===

def setup_scheduler(bot: Bot, user_id: int):
    # Основные опросы
    scheduler.add_job(morning_check, 'cron', hour=9, minute=0, args=[bot, user_id])
    scheduler.add_job(afternoon_check, 'cron', hour=14, minute=0, args=[bot, user_id])
    scheduler.add_job(evening_check, 'cron', hour=22, minute=0, args=[bot, user_id])
    scheduler.add_job(nag_user, 'cron', hour=23, minute=30, args=[bot, user_id])
    scheduler.add_job(weekly_report, 'cron', day_of_week='tue', hour=9, minute=0, args=[bot, user_id])
    scheduler.add_job(workout_reminder, 'interval', minutes=15, args=[bot, user_id])
    
    # Напоминания из расписания (таблетки/план)
    scheduler.add_job(schedule_morning_reminder, 'cron', hour=8, minute=0, args=[bot, user_id])
    scheduler.add_job(schedule_day_reminder, 'cron', hour=13, minute=0, args=[bot, user_id])
    scheduler.add_job(schedule_evening_reminder, 'cron', hour=21, minute=0, args=[bot, user_id])
    
    scheduler.start()
    print("✅ Scheduler запущен со всеми джобами")