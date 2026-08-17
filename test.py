import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM album;")
print("Album count:", cur.fetchone()[0])
cur.close()
conn.close()
