from datetime import datetime
from mongo_utils import connect_mongo

def insert_log(query, operation, result_summary, success=True):
    """
    Insert log entry into the logs collection
    """
    try:
        db = connect_mongo()
        log_entry = {
            "timestamp": datetime.now(),
            "user_query": query,
            "operation": operation,
            "result_summary": result_summary,
            "success": success
        }
        db.query_logs.insert_one(log_entry)
        return True
    except Exception as e:
        print(f"Error logging operation: {e}")
        return False 