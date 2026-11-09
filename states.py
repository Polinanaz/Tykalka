from aiogram.fsm.state import State, StatesGroup

class MorningStates(StatesGroup):
    sleep_quality = State()
    sport_planned = State()
    after_sport = State()  # После факта про спорт
    sweet_planned = State()
    after_sweet = State()  # После факта про сахар
    binge_details = State()

class EveningStates(StatesGroup):
    sweet_bool = State()
    sweet_type = State()
    sweet_other = State()
    sport_bool = State()
    sport_types = State()

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