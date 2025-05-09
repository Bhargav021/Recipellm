from SQL.db_utils import get_db_connection
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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
    except Exception as e:
        print(f"❌ Failed to log query: {e}")
