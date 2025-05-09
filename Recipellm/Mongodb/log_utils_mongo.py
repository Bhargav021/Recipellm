from pymongo import MongoClient
from datetime import datetime

def insert_log(user_query, action_type, generated_query, related_collection="N/A", matched=0, success=True):
    db = MongoClient("mongodb://localhost:27017/")["recipe_chatbot"]
    log_doc = {
        "timestamp": datetime.utcnow(),
        "user_query": user_query,
        "action_type": action_type,
        "generated_query": generated_query,
        "related_collection": related_collection,
        "matched_count": matched,
        "success": success
    }
    db.query_logs.insert_one(log_doc)
