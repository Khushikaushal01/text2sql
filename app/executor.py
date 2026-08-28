import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def execute_query(sql: str, timeout_ms: int = 5000, row_limit: int = 100):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.set_session(readonly=True)  # extra safety layer — DB-level read-only

    try:
        cur = conn.cursor()
        cur.execute(f"SET statement_timeout = {timeout_ms};")

        # add a LIMIT if the query doesn't already have one (basic safeguard)
        sql_to_run = sql.strip().rstrip(";")
        if "limit" not in sql_to_run.lower():
            sql_to_run += f" LIMIT {row_limit}"

        cur.execute(sql_to_run)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return {"columns": columns, "rows": rows}
    finally:
        cur.close()
        conn.close()