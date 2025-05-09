import psycopg2
import json

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def get_db_connection():
    config = load_config()
    return psycopg2.connect(
        dbname="recipe_chatbot",
        user="postgres",
        password=config["DB_PASSWORD"],
        host="localhost",
        port="5432"
    )

def execute_sql_query(sql_query):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        rows = cur.fetchall() if cur.description else []
        cols = [desc[0] for desc in cur.description] if cur.description else []
        return rows, cols
    finally:
        cur.close()
        conn.close()
