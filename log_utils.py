from db_utils import get_db_connection
from datetime import datetime

def insert_log(
    user_query,
    action_type,
    executed_sql,
    related_table=None,
    ingredient_id=None,
    recipe_id=None,
    price_id=None,
    success=True
):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO query_logs (
                timestamp,
                user_query,
                action_type,
                executed_sql,
                related_table,
                ingredient_id,
                recipe_id,
                price_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datetime.now(),
            user_query,
            f"{action_type}_{'SUCCESS' if success else 'FAIL'}",
            executed_sql,
            related_table,
            ingredient_id,
            recipe_id,
            price_id
        ))

        conn.commit()
        cur.close()
        conn.close()
        print("📝 Query successfully logged.")
    except Exception as e:
        print(f"❌ Failed to insert log: {e}")

def get_logs_by_status(success=True, limit=20):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        status = 'SUCCESS' if success else 'FAIL'
        cur.execute(f"""
            SELECT timestamp, user_query, action_type, executed_sql
            FROM query_logs
            WHERE action_type ILIKE %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (f'%{status}%', limit))

        logs = cur.fetchall()
        cur.close()
        conn.close()

        print(f"\n📋 {status} Logs:")
        for log in logs:
            print(f"⏱️  {log[0]}\n🧠  {log[1]}\n⚙️  {log[2]}\n📄  {log[3]}\n{'-'*40}")
        return logs

    except Exception as e:
        print(f"❌ Failed to retrieve logs: {e}")
        return []
