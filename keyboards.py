from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def sleep_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хорошо 😊", callback_data="sleep_good")],
        [InlineKeyboardButton(text="Плохо 😫", callback_data="sleep_bad")],
        [InlineKeyboardButton(text="Нормально 😐", callback_data="sleep_normal")]
    ])

def sport_planned_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Конечно 💪", callback_data="sport_yes")],
        [InlineKeyboardButton(text="Хочу, но лень 🛋️", callback_data="sport_lazy")],
        [InlineKeyboardButton(text="Неа 😴", callback_data="sport_no")]
    ])

def sweet_planned_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня без сладкого 💪", callback_data="sweet_no_plan")],  # <-- ДОБАВЬ подчёркивание
        [InlineKeyboardButton(text="Ну не знаю...", callback_data="sweet_unsure")],
        [InlineKeyboardButton(text="Сегодня срываюсь!", callback_data="sweet_binge")]
    ])

def sweet_bool_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да 🍬", callback_data="sweet_yes")],
        [InlineKeyboardButton(text="Нет 🙅‍♀️", callback_data="sweet_no")]
    ])

def sweet_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Шоколад 🍫", callback_data="type_choc")],
        [InlineKeyboardButton(text="Выпечка 🥐", callback_data="type_bak")],
        [InlineKeyboardButton(text="Конфета без сахара 🍬", callback_data="type_sugar_free")],
        [InlineKeyboardButton(text="Сладкий напиток 🥤", callback_data="type_drink")],
        [InlineKeyboardButton(text="Другое 🍰", callback_data="type_other")]
    ])

def sport_bool_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да 💪", callback_data="sport_yes_eve")],
        [InlineKeyboardButton(text="Нет 😔", callback_data="sport_no_eve")]
    ])

def sport_types_kb(selected=None):
    if selected is None:
        selected = []
    
    buttons = []
    types = [
        ("Бег 🏃‍♀️", "run"),
        ("Зал 🏋️‍♀️", "gym"),
        ("Физра 🏐", "pe"),
        ("Бассейн 🏊‍♀️", "pool"),
        ("Групповая тренировка 🤸‍♀️", "group"),
        ("Растяжка 🧘‍♀️", "stretch"),
        ("Другое ⚽", "other")
    ]
    
    for text, data in types:
        mark = "✅ " if data in selected else ""
        buttons.append([InlineKeyboardButton(text=f"{mark}{text}", callback_data=f"sport_{data}")])
    
    buttons.append([InlineKeyboardButton(text="Готово ✓", callback_data="sport_done")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def export_format_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="CSV 📊", callback_data="export_csv")],
        [InlineKeyboardButton(text="Excel 📈", callback_data="export_excel")]
    ])

# НОВЫЕ КЛАВИАТУРЫ

def continue_morning_kb():
    """Кнопка продолжить после факта про спорт"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дальше ➡️", callback_data="continue_morning")]
    ])

def sport_lazy_kb():
    """Кнопки после факта про спорт для ленивых"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ладно, пойду 💪", callback_data="go_sport_after_lazy")],
        [InlineKeyboardButton(text="Не, не пойду 😔", callback_data="continue_morning")]
    ])

def sweet_unsure_kb():
    """Кнопки после факта про сахар"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ок, без сладкого 💪", callback_data="no_sweet_after_unsure")],
        [InlineKeyboardButton(text="Все равно съем 🍰", callback_data="finish_morning")]
    ])

def finish_morning_kb():
    """Кнопка завершения утра"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить утро ✓", callback_data="finish_morning")]
    ])


def finish_with_review_kb():
    """Клавиатура в конце этапа с возможностью редактирования"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить ответы", callback_data="review_start")],
        [InlineKeyboardButton(text="Всё верно ✓", callback_data="review_done")]
    ])

def mood_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хорошее 😊", callback_data="mood_good")],
        [InlineKeyboardButton(text="Нормальное 😐", callback_data="mood_normal")],
        [InlineKeyboardButton(text="Плохое 😫", callback_data="mood_bad")]
    ])

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить ⏭️", callback_data="plan_skip")]
    ])

def daily_plan_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Напишу текстом ✍️", callback_data="plan_text")],
        [InlineKeyboardButton(text="Пропустить", callback_data="plan_skip")]
    ])


def review_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😴 Сон", callback_data="review_sleep")],
        [InlineKeyboardButton(text="💪 План спорт", callback_data="review_sport_plan")],
        [InlineKeyboardButton(text="🍬 План сладкое", callback_data="review_sweet_plan")],
        [InlineKeyboardButton(text="🍬 Факт сладкое", callback_data="review_sweet_fact")],
        [InlineKeyboardButton(text="💪 Факт спорт", callback_data="review_sport_fact")],
        [InlineKeyboardButton(text="⚖️ Вес", callback_data="review_weight")],
        [InlineKeyboardButton(text="😊 Настроение", callback_data="review_mood")],
        [InlineKeyboardButton(text="⏰ Время тренировки", callback_data="review_workout_time")],
        [InlineKeyboardButton(text="📝 План на день", callback_data="review_daily_plan")],
        [InlineKeyboardButton(text="Готово ✓", callback_data="review_done")]
    ])

def workout_plan_kb():
    """После ввода времени тренировки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Напишу план тренировки ✍️", callback_data="workout_plan_text")],
        [InlineKeyboardButton(text="Пропустить", callback_data="workout_plan_skip")]
    ])

def daily_plan_done_kb():
    """Вечером — что сделала из плана"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Всё сделала ✅", callback_data="daily_plan_all")],
        [InlineKeyboardButton(text="Часть сделала 🟡", callback_data="daily_plan_partial")],
        [InlineKeyboardButton(text="Ничего не сделала ❌", callback_data="daily_plan_none")]
    ])

def workout_done_kb():
    """Вечером — как прошла тренировка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выполнила план 💪", callback_data="workout_full")],
        [InlineKeyboardButton(text="Частично 🟡", callback_data="workout_partial")],
        [InlineKeyboardButton(text="Пропустила/не пошла ❌", callback_data="workout_skip")]
    ])