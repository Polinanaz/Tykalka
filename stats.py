import pandas as pd
from database import get_logs_for_period
from datetime import date

async def get_stats(user_id: int):
    logs = await get_logs_for_period(user_id, 7)
    
    if not logs:
        return "Нет данных за последнюю неделю"
    
    df = pd.DataFrame(logs)
    
    # Сладкое
    sweet_count = df['sweet_bool'].sum()
    sweet_types = df[df['sweet_bool'] == 1]['sweet_type'].value_counts()
    
    # Спорт
    sport_count = df['sport_bool'].sum()
    
    # Сон
    sleep_counts = df['sleep_quality'].value_counts()
    
    text = f"""
<b>Статистика за последние 7 дней:</b>

🍬 <b>Сладкое:</b> {sweet_count} раз из 7
"""
    
    for stype, count in sweet_types.items():
        text += f"   - {stype}: {count}\n"
    
    text += f"\n💪 <b>Спорт:</b> {sport_count} раз из 7\n"
    
    text += f"\n😴 <b>Сон:</b>\n"
    for quality, count in sleep_counts.items():
        text += f"   - {quality}: {count}\n"
    
    # Тренды
    prev_logs = await get_logs_for_period(user_id, 14)
    if len(prev_logs) > 7:
        prev_df = pd.DataFrame(prev_logs[:7])
        prev_sweet = prev_df['sweet_bool'].sum()
        
        if prev_sweet > 0 and sweet_count < prev_sweet:
            text += f"\n📉 <b>Тренд:</b> Меньше сладкого ({int((1 - sweet_count/prev_sweet)*100)}% снижение)!"
    
    return text