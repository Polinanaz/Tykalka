from aiogram.fsm.state import State, StatesGroup

class MorningStates(StatesGroup):
    sleep_quality = State()
    sport_planned = State()
    after_sport = State()
    sweet_planned = State()
    after_sweet = State()
    binge_details = State()
    workout_time = State()
    workout_plan = State()          # <-- ДОБАВЛЕНО
    workout_plan_text = State()     # <-- ДОБАВЛЕНО
    daily_plan = State()
    daily_plan_text = State()

class EveningStates(StatesGroup):
    sweet_bool = State()
    sweet_type = State()
    sweet_other = State()
    sport_bool = State()
    sport_types = State()
    after_sport = State()
    daily_plan_fact = State()       # <-- ДОБАВЛЕНО
    daily_plan_fact_text = State()  # <-- ДОБАВЛЕНО
    workout_fact = State()          # <-- ДОБАВЛЕНО
    workout_fact_text = State()     # <-- ДОБАВЛЕНО

class WeightStates(StatesGroup):
    waiting_weight = State()

class ReviewStates(StatesGroup):
    waiting_action = State()
    editing_sleep = State()
    editing_sport_plan = State()
    editing_sweet_plan = State()
    editing_sweet_fact = State()
    editing_sweet_type = State()
    editing_sport_fact = State()
    editing_sport_types = State()
    editing_weight = State()
    editing_mood = State()
    editing_workout_time = State()
    editing_daily_plan = State()
    editing_workout_plan = State()  # <-- ДОБАВЛЕНО
    editing_daily_plan_fact = State()  # <-- ДОБАВЛЕНО
    editing_daily_plan_fact_text = State()  # <-- ДОБАВЛЕНО
    editing_workout_fact = State()  # <-- ДОБАВЛЕНО
    editing_workout_fact_text = State()  # <-- ДОБАВЛЕНО

class ScheduleStates(StatesGroup):
    choosing_day = State()
    waiting_morning = State()
    waiting_day = State()
    waiting_evening = State()