import sqlite3
import pandas as pd
import datetime

conn = sqlite3.connect("food_log.db")

# Calculate the dates for today and the previous two days
today = datetime.date.today()
dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(3)]  # 0,1,2 days ago

query = f'''
SELECT * FROM food_log WHERE date IN ({','.join(['?']*len(dates))})
ORDER BY date DESC
'''

df = pd.read_sql_query(query, conn, params=dates)
print(df)

conn.close()
