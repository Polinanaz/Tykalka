from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import save_log, update_log, get_today_log, get_current_day
import os
import random

from states import MorningStates, EveningStates, WeightStates, ReviewStates
from keyboards import *
from database import save_log, update_log, get_today_log, get_current_day
from facts import get_random_sport_fact, get_random_sugar_fact
from export import export_data
from stats import get_stats

router = Router()

# === ПОЖЕЛАНИЯ ===

DAY_WISHES = [
    "Успешного дня! 💫",
    "Хорошего дня! ☀️",
    "Замечательного дня! 🌟",
    "Продуктивного дня! 🚀",
    "Отличного дня! 🎯",
    "Яркого дня! ✨",
    "Классного дня! 🎉"
]

NIGHT_WISHES = [
    "Спокойной ночи! 🌙",
    "Доброй ночи! 😴",
    "Сладких снов! 💤",
    "Приятных снов! 🌟",
    "Хорошо отдохни! 🛌",
    "До завтра! 👋"
]

def get_day_wish():
    return random.choice(DAY_WISHES)

def get_night_wish():
    return random.choice(NIGHT_WISHES)

# === МАППИНГ ЗНАЧЕНИЙ (текст БЕЗ эмодзи для курсива, эмодзи отдельно) ===

SLEEP_MAP = {
    "good": ("Хорошо", "😊"),
    "bad": ("Плохо", "😫"),
    "normal": ("Нормально", "😐")
}

SPORT_PLAN_MAP = {
    "yes": ("Конечно", "💪"),
    "lazy": ("Хочу, но лень", "🛋️"),
    "no": ("Неа", "😴")
}

SWEET_PLAN_MAP = {
    "no_plan": ("Сегодня без сладкого", "💪"),
    "unsure": ("Ну не знаю...", "🤔"),
    "binge": ("Сегодня срываюсь!", "🍰")
}

SWEET_TYPE_MAP = {
    "choc": ("Шоколад", "🍫"),
    "bak": ("Выпечка", "🥐"),
    "sugar_free": ("Конфета без сахара", "🍬"),
    "drink": ("Сладкий напиток", "🥤"),
    "none": ("Не ела", "🙅‍♀️")
}

SPORT_TYPE_MAP = {
    "run": "Бег 🏃‍♀️",
    "gym": "Зал 🏋️‍♀️",
    "pe": "Физра 🏐",
    "pool": "Бассейн 🏊‍♀️",
    "group": "Групповая 🤸‍♀️",
    "stretch": "Растяжка 🧘‍♀️",
    "other": "Другое ⚽"
}

MOOD_MAP = {
    "good": "Хорошее 😊",
    "normal": "Нормальное 😐",
    "bad": "Плохое 😫"
}

def format_value(field: str, value) -> str:
    if value is None or value == "None" or value == "":
        return "не отмечено"
    
    if field == "sleep_quality":
        text, emoji = SLEEP_MAP.get(value, (value, ""))
        return f"{text} {emoji}"
    elif field == "sport_planned":
        text, emoji = SPORT_PLAN_MAP.get(value, (value, ""))
        return f"{text} {emoji}"
    elif field == "sweet_planned":
        text, emoji = SWEET_PLAN_MAP.get(value, (value, ""))
        return f"{text} {emoji}"
    elif field == "sweet_type":
        if str(value).startswith("other:"):
            return f"Другое: {value[6:]}"
        text, emoji = SWEET_TYPE_MAP.get(value, (value, ""))
        return f"{text} {emoji}"
    elif field == "sport_types":
        if isinstance(value, str):
            try:
                value = eval(value)
            except:
                value = []
        if isinstance(value, list):
            return ", ".join([SPORT_TYPE_MAP.get(v, v) for v in value]) if value else "не отмечено"
        return "не отмечено"
    elif field == "mood":
        return MOOD_MAP.get(value, value)
    
    return str(value)

def get_answer_text(field_map, key):
    """Возвращает (текст_без_эмодзи, эмодзи) для курсива"""
    if key in field_map:
        return field_map[key]
    return (str(key), "")

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

async def show_review_screen(message, user_id: int, state: FSMContext):
    today = get_current_day()
    log = await get_today_log(user_id, today)
    
    if not log:
        await message.answer("Сегодня еще нет записей. Начни с /start")
        return
    
    text = "<b>Твои ответы за сегодня:</b>\n\n"
    text += f"😴 <b>Как спалось:</b> {format_value('sleep_quality', log.get('sleep_quality'))}\n"
    text += f"💪 <b>План на спорт:</b> {format_value('sport_planned', log.get('sport_planned'))}\n"
    text += f"🍬 <b>План по сладкому:</b> {format_value('sweet_planned', log.get('sweet_planned'))}\n"
    text += f"🍬 <b>Ела ли сладкое (факт):</b> {format_value('sweet_type', log.get('sweet_type'))}\n"
    text += f"💪 <b>Была ли тренировка (факт):</b> {format_value('sport_types', log.get('sport_types'))}\n"
    text += f"⚖️ <b>Вес:</b> {log.get('weight', 'не отмечено')}\n"
    text += f"\nНажми на поле, которое хочешь изменить:"
    
    await state.set_state(ReviewStates.waiting_action)
    await message.answer(text, parse_mode="HTML", reply_markup=review_kb())

# === КОМАНДЫ ===

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Доброе утро! Как спалось?", reply_markup=sleep_kb())
    await state.set_state(MorningStates.sleep_quality)

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Сброшено. Начни заново: /start")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = """
/start — Начать день
/weight — Записать вес
/review — Просмотреть и изменить ответы
/export — Выгрузить данные
/stats — Статистика за неделю
/reset — Сбросить текущий опрос
    """
    await message.answer(text)

@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    await message.answer("Сколько кг?")
    await state.set_state(WeightStates.waiting_weight)

@router.message(StateFilter(WeightStates.waiting_weight))
async def process_weight(message: Message, state: FSMContext):
    today = get_current_day()
    await update_log(message.from_user.id, today, weight=message.text)
    await state.clear()
    await message.answer(f"Записала: {message.text} кг ✅")

@router.message(Command("export"))
async def cmd_export(message: Message):
    await message.answer("В каком формате?", reply_markup=export_format_kb())

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = await get_stats(message.from_user.id)
    await message.answer(stats, parse_mode="HTML")

@router.message(Command("review"))
async def cmd_review(message: Message, state: FSMContext):
    await show_review_screen(message, message.from_user.id, state)

# === ОБРАБОТКА КНОПКИ "ИЗМЕНИТЬ ОТВЕТЫ" ===

@router.callback_query(F.data == "review_start")
async def start_review_from_finish(call: CallbackQuery, state: FSMContext):
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

@router.callback_query(F.data == "review_done")
async def finish_review(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # Редактируем сообщение с кнопками и убираем их
    await call.message.edit_text(
        "Отлично! Если нужно что-то изменить — напиши /review ✏️",
        reply_markup=None  # УБИРАЕМ КНОПКИ
    )
    await call.answer()

# === РЕДАКТИРОВАНИЕ ОТВЕТОВ ===

@router.callback_query(F.data == "review_sleep")
async def edit_sleep_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Как спалось?", reply_markup=sleep_kb())
    await state.set_state(ReviewStates.editing_sleep)
    await call.answer()

@router.callback_query(F.data == "review_sport_plan")
async def edit_sport_plan_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("На спорт пойдешь?", reply_markup=sport_planned_kb())
    await state.set_state(ReviewStates.editing_sport_plan)
    await call.answer()

@router.callback_query(F.data == "review_sweet_plan")
async def edit_sweet_plan_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Постараешься не есть сладкое?", reply_markup=sweet_planned_kb())
    await state.set_state(ReviewStates.editing_sweet_plan)
    await call.answer()

@router.callback_query(F.data == "review_sweet_fact")
async def edit_sweet_fact_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Ты сегодня ела сладкое?", reply_markup=sweet_bool_kb())
    await state.set_state(ReviewStates.editing_sweet_fact)
    await call.answer()

@router.callback_query(F.data == "review_sport_fact")
async def edit_sport_fact_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Был ли сегодня спорт?", reply_markup=sport_bool_kb())
    await state.set_state(ReviewStates.editing_sport_fact)
    await call.answer()

@router.callback_query(F.data == "review_weight")
async def edit_weight_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Сколько кг? Напиши число.")
    await state.set_state(ReviewStates.editing_weight)
    await call.answer()

# Редактирование сна
@router.callback_query(F.data.startswith("sleep_"), StateFilter(ReviewStates.editing_sleep))
async def edit_sleep(call: CallbackQuery, state: FSMContext):
    quality = call.data.split("_")[1]
    today = get_current_day()
    await update_log(call.from_user.id, today, sleep_quality=quality)
    text, emoji = get_answer_text(SLEEP_MAP, quality)
    await call.message.edit_text(
        f"Как спалось?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None  # УБИРАЕМ КНОПКИ
    )
    await call.message.answer(f"Сон обновлен: {text} {emoji} ✅")
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

# Редактирование плана на спорт
@router.callback_query(F.data.startswith("sport_"), StateFilter(ReviewStates.editing_sport_plan))
async def edit_sport_plan(call: CallbackQuery, state: FSMContext):
    planned = call.data.split("_")[1]
    today = get_current_day()
    await update_log(call.from_user.id, today, sport_planned=planned)
    text, emoji = get_answer_text(SPORT_PLAN_MAP, planned)
    await call.message.edit_text(
        f"На спорт пойдешь?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer(f"План на спорт обновлен: {text} {emoji} ✅")
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

# Редактирование плана на сладкое
@router.callback_query(F.data.startswith("sweet_"), StateFilter(ReviewStates.editing_sweet_plan))
async def edit_sweet_plan(call: CallbackQuery, state: FSMContext):
    planned = call.data.split("_")[1]
    today = get_current_day()
    await update_log(call.from_user.id, today, sweet_planned=planned)
    text, emoji = get_answer_text(SWEET_PLAN_MAP, planned)
    await call.message.edit_text(
        f"Постараешься не есть сладкое?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer(f"План по сладкому обновлен: {text} {emoji} ✅")
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

# Редактирование факта о сладком
@router.callback_query(F.data == "sweet_yes", StateFilter(ReviewStates.editing_sweet_fact))
async def edit_sweet_fact_yes(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Что именно?", reply_markup=sweet_type_kb())
    await state.set_state(ReviewStates.editing_sweet_type)
    await call.answer()

@router.callback_query(F.data == "sweet_no", StateFilter(ReviewStates.editing_sweet_fact))
async def edit_sweet_fact_no(call: CallbackQuery, state: FSMContext):
    today = get_current_day()
    await update_log(call.from_user.id, today, sweet_bool=False, sweet_type="none")
    await call.message.edit_text(
        "Ты сегодня ела сладкое?\n<i>Нет</i> 🙅‍♀️",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Обновлено: без сладкого ✅")
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

@router.callback_query(F.data.startswith("type_"), StateFilter(ReviewStates.editing_sweet_type))
async def edit_sweet_type(call: CallbackQuery, state: FSMContext):
    sweet_type = call.data.split("_")[1]
    today = get_current_day()
    await update_log(call.from_user.id, today, sweet_bool=True, sweet_type=sweet_type)
    text, emoji = get_answer_text(SWEET_TYPE_MAP, sweet_type)
    await call.message.edit_text(
        f"Что именно?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer(f"Тип сладкого обновлен: {text} {emoji} ✅")
    await show_review_screen(call.message, call.from_user.id, state)
    await call.answer()

# Редактирование факта о спорте
@router.callback_query(F.data == "sport_yes_eve", StateFilter(ReviewStates.editing_sport_fact))
async def edit_sport_fact_yes(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Что делала? (можно выбрать несколько)", reply_markup=sport_types_kb())
    await state.update_data(temp_sport_types=[])
    await state.set_state(ReviewStates.editing_sport_types)
    await call.answer()

@router.callback_query(F.data == "sport_no_eve", StateFilter(ReviewStates.editing_sport_fact))
async def edit_sport_fact_no(call: CallbackQuery, state: FSMContext):
    today = get_current_day()
    
    # Сначала обновляем базу
    await update_log(call.from_user.id, today, sport_bool=False, sport_types="[]")
    
    # Потом редактируем сообщение с кнопками — убираем их
    await call.message.edit_text(
        "Был ли сегодня спорт?\n<i>Нет</i> 😔",
        parse_mode="HTML",
        reply_markup=None  # Явно убираем кнопки
    )
    
    # Отправляем подтверждение
    await call.message.answer("Обновлено: без спорта ✅")
    
    # Показываем экран review
    await show_review_screen(call.message, call.from_user.id, state)
    
    await call.answer()

@router.callback_query(F.data.startswith("sport_"), StateFilter(ReviewStates.editing_sport_types))
async def edit_sport_types(call: CallbackQuery, state: FSMContext):
    if call.data == "sport_done":
        data = await state.get_data()
        sport_types = data.get("temp_sport_types", [])
        today = get_current_day()
        await update_log(call.from_user.id, today, sport_bool=True, sport_types=str(sport_types))
        types_text = ", ".join([SPORT_TYPE_MAP.get(s, s) for s in sport_types]) if sport_types else "ничего"
        
        # Редактируем сообщение с кнопками и убираем их
        await call.message.edit_text(
            f"Что делала? (можно выбрать несколько)\n<i>{types_text}</i>",
            parse_mode="HTML",
            reply_markup=None  # УБИРАЕМ КНОПКИ
        )
        
        await call.message.answer(f"Спорт обновлен: {types_text} ✅")
        await show_review_screen(call.message, call.from_user.id, state)
        await call.answer()
        return
    
    sport_type = call.data.split("_")[1]
    data = await state.get_data()
    selected = data.get("temp_sport_types", [])
    
    if sport_type in selected:
        selected.remove(sport_type)
    else:
        selected.append(sport_type)
    
    await state.update_data(temp_sport_types=selected)
    await call.message.edit_reply_markup(reply_markup=sport_types_kb(selected))
    await call.answer()

# Редактирование веса
@router.message(StateFilter(ReviewStates.editing_weight))
async def edit_weight(message: Message, state: FSMContext):
    today = get_current_day()
    await update_log(message.from_user.id, today, weight=message.text)
    await message.answer(f"Вес обновлен: {message.text} кг ✅")
    await show_review_screen(message, message.from_user.id, state)

# === УТРЕННИЙ СЦЕНАРИЙ ===

@router.callback_query(F.data.startswith("sleep_"))
async def process_sleep(call: CallbackQuery, state: FSMContext):
    quality = call.data.split("_")[1]
    await state.update_data(sleep_quality=quality)
    text, emoji = get_answer_text(SLEEP_MAP, quality)
    await call.message.edit_text(
        f"Доброе утро! Как спалось?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None  # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ
    )
    await call.message.answer("На спорт пойдешь?", reply_markup=sport_planned_kb())
    await state.set_state(MorningStates.sport_planned)
    await call.answer()

@router.callback_query(F.data.startswith("sport_"), StateFilter(MorningStates.sport_planned))
async def process_sport_planned(call: CallbackQuery, state: FSMContext):
    planned = call.data.split("_")[1]
    await state.update_data(sport_planned=planned)
    text, emoji = get_answer_text(SPORT_PLAN_MAP, planned)
    
    await call.message.edit_text(
        f"На спорт пойдешь?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    
    if planned == "yes":
        await call.message.answer("Молодец! Удачи на тренировке 💪", reply_markup=continue_morning_kb())
    elif planned == "lazy":
        fact = get_random_sport_fact()
        await call.message.answer(f"{fact}\n\nДавай хотя бы 10 минут прогулки? Это реально!", reply_markup=sport_lazy_kb())
    else:
        await call.message.answer("Ок. Тогда постарайся пройти 10к шагов и активно учиться 📚", reply_markup=continue_morning_kb())
    
    await state.set_state(MorningStates.after_sport)
    await call.answer()

@router.callback_query(F.data == "continue_morning", StateFilter(MorningStates.after_sport))
async def continue_after_sport(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        call.message.text + "\n<i>Дальше ➡️</i>",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Постараешься не есть сладкое?", reply_markup=sweet_planned_kb())
    await state.set_state(MorningStates.sweet_planned)
    await call.answer()

@router.callback_query(F.data == "go_sport_after_lazy", StateFilter(MorningStates.after_sport))
async def go_sport_after_lazy(call: CallbackQuery, state: FSMContext):
    await state.update_data(sport_planned="yes")
    await call.message.edit_text(
        call.message.text + "\n<i>Ладно, пойду 💪</i>",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Отлично! Удачи на тренировке 💪", reply_markup=continue_morning_kb())
    await call.answer()

@router.callback_query(F.data.startswith("sweet_"), StateFilter(MorningStates.sweet_planned))
async def process_sweet_planned(call: CallbackQuery, state: FSMContext):
    planned = call.data.split("_")[1]
    await state.update_data(sweet_planned=planned)
    text, emoji = get_answer_text(SWEET_PLAN_MAP, planned)
    
    await call.message.edit_text(
        f"Постараешься не есть сладкое?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    
    if planned == "no_plan":
        await call.message.answer("Отлично! Держись 💪", reply_markup=finish_morning_kb())
    elif planned == "unsure":
        fact = get_random_sugar_fact()
        await call.message.answer(f"{fact}\n\nПодумай, оно того стоит?", reply_markup=sweet_unsure_kb())
    else:  # binge
        await call.message.answer("На что срываешься? И сколько планируешь съесть?")
        await state.set_state(MorningStates.binge_details)
        await call.answer()
        return
    
    await state.set_state(MorningStates.after_sweet)
    await call.answer()

@router.callback_query(F.data == "no_sweet_after_unsure", StateFilter(MorningStates.after_sweet))
async def no_sweet_after_unsure(call: CallbackQuery, state: FSMContext):
    await state.update_data(sweet_planned="no_plan")
    text, emoji = get_answer_text(SWEET_PLAN_MAP, "no_plan")
    await call.message.edit_text(
        f"Постараешься не есть сладкое?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Отлично! Держись 💪", reply_markup=finish_morning_kb())
    await state.set_state(MorningStates.after_sweet)
    await call.answer()

@router.callback_query(F.data == "finish_morning", StateFilter(MorningStates.after_sweet))
async def finish_morning(call: CallbackQuery, state: FSMContext):
    today = get_current_day()
    data = await state.get_data()
    await update_log(call.from_user.id, today, 
                     sleep_quality=data.get("sleep_quality"),
                     sport_planned=data.get("sport_planned"),
                     sweet_planned=data.get("sweet_planned"))
    
    await state.clear()
    
    # Редактируем сообщение с кнопкой "Завершить утро" и убираем её
    await call.message.edit_text(
        "Постараешься не есть сладкое?\n<i>Завершить утро ✓</i>",
        parse_mode="HTML",
        reply_markup=None  # УБИРАЕМ КНОПКИ
    )
    
    await call.message.answer(
        f"Утро записано ✅\n\n{get_day_wish()}\n\nЕсли хочешь что-то изменить — нажми кнопку ниже.",
        reply_markup=finish_with_review_kb()
    )
    await call.answer()
@router.message(StateFilter(MorningStates.binge_details))
async def process_binge_details(message: Message, state: FSMContext):
    today = get_current_day()
    data = await state.get_data()
    
    # ИЗМЕНЕНО: save_log -> update_log
    await update_log(message.from_user.id, today,
                     sleep_quality=data.get("sleep_quality"),
                     sport_planned=data.get("sport_planned"),
                     sweet_planned="binge",
                     notes=f"Binge: {message.text}")
                     
    await state.clear()
    await message.answer(
        f"Записала. Постарайся контролировать порцию 🍽️\n\n{get_day_wish()}\n\nЕсли хочешь что-то изменить — напиши /review",
        reply_markup=finish_with_review_kb()
    )

# === ВЕЧЕРНИЙ СЦЕНАРИЙ ===

@router.callback_query(F.data == "sweet_yes")
async def process_sweet_yes(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Ты сегодня ела сладкое?\n<i>Да</i> 🍬",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Завидую...а что именно?", reply_markup=sweet_type_kb())
    await state.set_state(EveningStates.sweet_type)
    await call.answer()

@router.callback_query(F.data == "sweet_no")
async def process_sweet_no(call: CallbackQuery, state: FSMContext):
    await state.update_data(sweet_bool=False, sweet_type="none")
    await call.message.edit_text(
        "Ты сегодня ела сладкое?\n<i>Нет</i> 🙅‍♀️",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Был ли сегодня спорт?", reply_markup=sport_bool_kb())
    await state.set_state(EveningStates.sport_bool)
    await call.answer()

@router.callback_query(F.data.startswith("type_"), StateFilter(EveningStates.sweet_type))
async def process_sweet_type(call: CallbackQuery, state: FSMContext):
    sweet_type = call.data.split("_")[1]
    
    if sweet_type == "other":
        await call.message.answer("Что именно?")
        await state.set_state(EveningStates.sweet_other)
        await call.answer()
        return
    
    await state.update_data(sweet_bool=True, sweet_type=sweet_type)
    text, emoji = get_answer_text(SWEET_TYPE_MAP, sweet_type)
    await call.message.edit_text(
        f"Завидую...а что именно?\n<i>{text}</i> {emoji}",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Был ли сегодня спорт?", reply_markup=sport_bool_kb())
    await state.set_state(EveningStates.sport_bool)
    await call.answer()

@router.message(StateFilter(EveningStates.sweet_other))
async def process_sweet_other(message: Message, state: FSMContext):
    await state.update_data(sweet_bool=True, sweet_type=f"other:{message.text}")
    await message.answer("Был ли сегодня спорт?", reply_markup=sport_bool_kb())
    await state.set_state(EveningStates.sport_bool)

@router.callback_query(F.data == "sport_yes_eve")
async def process_sport_yes(call: CallbackQuery, state: FSMContext):
    await state.update_data(sport_bool=True, sport_types=[])
    await call.message.edit_text(
        "Был ли сегодня спорт?\n<i>Да</i> 💪",
        parse_mode="HTML",
        reply_markup=None
    )
    await call.message.answer("Что делала? (можно выбрать несколько)", reply_markup=sport_types_kb())
    await state.set_state(EveningStates.sport_types)
    await call.answer()

@router.callback_query(F.data == "sport_no_eve")
async def process_sport_no(call: CallbackQuery, state: FSMContext):
    await state.update_data(sport_bool=False, sport_types=[])
    await call.message.edit_text(
        "Был ли сегодня спорт?\n<i>Нет</i> 😔",
        parse_mode="HTML",
        reply_markup=None
    )
    await finish_day(call, state)
    await call.answer()

@router.callback_query(F.data.startswith("sport_"), StateFilter(EveningStates.sport_types))
async def process_sport_types(call: CallbackQuery, state: FSMContext):
    if call.data == "sport_done":
        data = await state.get_data()
        sport_types = data.get("sport_types", [])
        types_text = ", ".join([SPORT_TYPE_MAP.get(s, s) for s in sport_types]) if sport_types else "ничего"
        
        # Редактируем сообщение с кнопками и убираем их
        await call.message.edit_text(
            f"Что делала? (можно выбрать несколько)\n<i>{types_text}</i>",
            parse_mode="HTML",
            reply_markup=None  # УБИРАЕМ КНОПКИ
        )
        
        await finish_day(call, state)
        await call.answer()
        return
    
    sport_type = call.data.split("_")[1]
    data = await state.get_data()
    selected = data.get("sport_types", [])
    
    if sport_type in selected:
        selected.remove(sport_type)
    else:
        selected.append(sport_type)
    
    await state.update_data(sport_types=selected)
    await call.message.edit_reply_markup(reply_markup=sport_types_kb(selected))
    await call.answer()

async def finish_day(call: CallbackQuery, state: FSMContext):
    today = get_current_day()
    data = await state.get_data()
    
    await update_log(call.from_user.id, today,
                     sweet_bool=data.get("sweet_bool"),
                     sweet_type=data.get("sweet_type"),
                     sport_bool=data.get("sport_bool"),
                     sport_types=str(data.get("sport_types", [])))
    
    await state.clear()
    
    # Редактируем сообщение с кнопками и убираем их
    await call.message.edit_text(
        "День записан ✅",
        reply_markup=None  # УБИРАЕМ КНОПКИ
    )
    
    await call.message.answer(
        f"{get_night_wish()}\n\nЕсли хочешь что-то изменить — нажми кнопку ниже.",
        reply_markup=finish_with_review_kb()
    )

# === ВЫГРУЗКА ===

@router.callback_query(F.data.startswith("export_"))
async def process_export(call: CallbackQuery):
    fmt = call.data.split("_")[1]
    filename = await export_data(call.from_user.id, fmt)
    await call.message.answer_document(FSInputFile(filename))
    os.remove(filename)
    await call.answer()

# === НАСТРОЕНИЕ (ДНЕВНОЕ НАПОМИНАНИЕ) ===

@router.callback_query(F.data.startswith("mood_"))
async def process_mood(call: CallbackQuery, state: FSMContext):
    mood = call.data.split("_")[1]
    today = get_current_day()
    await update_log(call.from_user.id, today, mood=mood)
    
    responses = {
        "good": "Супер! Хорошее настроение — это важно 😊",
        "normal": "Нормально — тоже хорошо. Держись! 💪",
        "bad": "Понимаю. Помни: это временно. Завтра будет лучше 🌟"
    }
    
    await call.message.answer(responses.get(mood, "Записала!"))
    await call.answer()

@router.callback_query(F.data == "evening_start")
async def start_evening_survey(call: CallbackQuery, state: FSMContext):
    """Запуск вечернего опросника по кнопке"""
    await call.message.edit_text(
        "Ты сегодня ела сладкое?",
        reply_markup=sweet_bool_kb()
    )
    await state.set_state(EveningStates.sweet_bool)
    await call.answer()