import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "screen_time.db")

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
cur.execute("SELECT * FROM daily_usage")
print(cur.fetchall())