import psycopg2
import json
import os
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "recipe_chatbot"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def execute_sql_query(sql_query):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        conn.commit()  
        rows = cur.fetchall() if cur.description else []
        cols = [desc[0] for desc in cur.description] if cur.description else []
        return rows, cols
    finally:
        cur.close()
        conn.close()
