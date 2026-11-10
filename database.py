import aiosqlite
from datetime import date, datetime, time, timedelta

DB_PATH = "diet_bot.db"


def get_current_day() -> date:
    """Возвращает 'логическую' дату дня. Новый день начинается в 06:00."""
    now = datetime.now()
    if now.time() < time(6, 0):
        return (now - timedelta(days=1)).date()
    return now.date()


def parse_workout_time(time_str: str) -> datetime | None:
    """Парсит строку 'HH:MM' и возвращает datetime на сегодня с этим временем."""
    if not time_str:
        return None
    try:
        time_obj = datetime.strptime(time_str.strip(), "%H:%M").time()
        today = get_current_day()
        return datetime.combine(today, time_obj)
    except ValueError:
        return None


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                sleep_quality TEXT,
                sport_planned TEXT,
                sweet_planned TEXT,
                sweet_bool INTEGER,
                sweet_type TEXT,
                sport_bool INTEGER,
                sport_types TEXT,
                weight TEXT,
                mood TEXT,
                notes TEXT,
                workout_time TEXT,
                daily_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()


async def save_log(user_id: int, log_date: date, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        columns = ['user_id', 'date'] + list(kwargs.keys())
        values = [user_id, str(log_date)] + list(kwargs.values())
        placeholders = ', '.join(['?' for _ in values])
        column_names = ', '.join(columns)
        await db.execute(
            f'INSERT INTO daily_logs ({column_names}) VALUES ({placeholders})',
            values
        )
        await db.commit()


async def update_log(user_id: int, log_date: date, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT id FROM daily_logs WHERE user_id = ? AND date = ?',
            (user_id, str(log_date))
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id, str(log_date)]
            await db.execute(
                f'UPDATE daily_logs SET {set_clause} WHERE user_id = ? AND date = ?',
                values
            )
        else:
            columns = ['user_id', 'date'] + list(kwargs.keys())
            values = [user_id, str(log_date)] + list(kwargs.values())
            placeholders = ', '.join(['?' for _ in values])
            column_names = ', '.join(columns)
            await db.execute(
                f'INSERT INTO daily_logs ({column_names}) VALUES ({placeholders})',
                values
            )
        await db.commit()


async def get_today_log(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = get_current_day()
        async with db.execute(
            'SELECT * FROM daily_logs WHERE user_id = ? AND date = ?',
            (user_id, str(today))
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_logs_for_period(user_id: int, days: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        end_date = get_current_day()
        start_date = end_date - timedelta(days=days)

        async with db.execute(
            'SELECT * FROM daily_logs WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date',
            (user_id, str(start_date), str(end_date))
        ) as cursor:
            rows = await cursor.fetchall()
            logs = []
            for row in rows:
                log = dict(row)
                if log.get('sport_types'):
                    try:
                        log['sport_types'] = eval(log['sport_types'])
                    except:
                        log['sport_types'] = []
                logs.append(log)
            return logs


async def clear_database():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM daily_logs')
        await db.commit()
    print("База данных полностью очищена")


async def remove_duplicates():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT user_id, date, MAX(id) as max_id
            FROM daily_logs
            GROUP BY user_id, date
            HAVING COUNT(*) > 1
        ''') as cursor:
            duplicates = await cursor.fetchall()

        if not duplicates:
            print("Дубликатов не найдено")
            return

        for user_id, log_date, max_id in duplicates:
            await db.execute(
                'DELETE FROM daily_logs WHERE user_id = ? AND date = ? AND id != ?',
                (user_id, log_date, max_id)
            )
        await db.commit()
        print(f"Удалено дубликатов: {len(duplicates)}")

async def migrate_db():
    """Добавляет недостающие колонки"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("PRAGMA table_info(daily_logs)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
        
        new_columns = {
            'workout_time': "ALTER TABLE daily_logs ADD COLUMN workout_time TEXT",
            'daily_plan': "ALTER TABLE daily_logs ADD COLUMN daily_plan TEXT",
            'workout_plan': "ALTER TABLE daily_logs ADD COLUMN workout_plan TEXT",
            'daily_plan_fact': "ALTER TABLE daily_logs ADD COLUMN daily_plan_fact TEXT",
            'workout_fact': "ALTER TABLE daily_logs ADD COLUMN workout_fact TEXT",
        }
        
        for col, sql in new_columns.items():
            if col not in columns:
                await db.execute(sql)
                print(f"Добавлена колонка {col}")
        
        await db.commit()