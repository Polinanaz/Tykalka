import aiosqlite
from datetime import date, datetime, time, timedelta
from pathlib import Path

DB_PATH = "diet_bot.db"

def get_current_day() -> date:
    """
    Возвращает 'логическую' дату дня.
    Новый день начинается в 06:00, а не в 00:00.
    """
    now = datetime.now()
    if now.time() < time(6, 0):
        return (now - timedelta(days=1)).date()
    return now.date()

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def save_log(user_id: int, date: date, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        columns = ['user_id', 'date'] + list(kwargs.keys())
        values = [user_id, date] + list(kwargs.values())
        
        placeholders = ', '.join(['?' for _ in values])
        column_names = ', '.join(columns)
        
        await db.execute(f'''
            INSERT INTO daily_logs ({column_names}) VALUES ({placeholders})
        ''', values)
        await db.commit()

async def update_log(user_id: int, date: date, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем, есть ли запись за сегодня
        async with db.execute('''
            SELECT id FROM daily_logs WHERE user_id = ? AND date = ?
        ''', (user_id, date)) as cursor:
            row = await cursor.fetchone()
        
        if row:
            # Обновляем существующую
            set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id, date]
            
            await db.execute(f'''
                UPDATE daily_logs SET {set_clause}
                WHERE user_id = ? AND date = ?
            ''', values)
        else:
            # Создаем новую
            columns = ['user_id', 'date'] + list(kwargs.keys())
            values = [user_id, date] + list(kwargs.values())
            
            placeholders = ', '.join(['?' for _ in values])
            column_names = ', '.join(columns)
            
            await db.execute(f'''
                INSERT INTO daily_logs ({column_names}) VALUES ({placeholders})
            ''', values)
        
        await db.commit()

async def get_today_log(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = get_current_day()  # <-- ИЗМЕНЕНО
        async with db.execute('''
            SELECT * FROM daily_logs WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_logs_for_period(user_id: int, days: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        end_date = get_current_day()  # <-- ИЗМЕНЕНО
        start_date = end_date - timedelta(days=days)
        
        async with db.execute('''
            SELECT * FROM daily_logs 
            WHERE user_id = ? AND date >= ? AND date <= ?
            ORDER BY date
        ''', (user_id, start_date, end_date)) as cursor:
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