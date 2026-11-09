import pandas as pd
from datetime import datetime
from database import get_logs_for_period

async def export_data(user_id: int, format: str):
    logs = await get_logs_for_period(user_id, 365)
    
    df = pd.DataFrame(logs)
    filename = f"polya_diet_{datetime.now().strftime('%Y-%m-%d')}"
    
    if format == "csv":
        filepath = f"{filename}.csv"
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
    else:  # excel
        filepath = f"{filename}.xlsx"
        df.to_excel(filepath, index=False)
    
    return filepath