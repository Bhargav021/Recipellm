from pymongo import MongoClient
import json
import re
import os
from dotenv import load_dotenv

client = MongoClient("mongodb://localhost:27017/")
db = client["recipe_chatbot"]

def connect_mongo():
    return db

def load_config():
    load_dotenv()
    return {
        "API_KEY": os.getenv("LLM_API_KEY", ""),
        "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        "DB_NAME": os.getenv("DB_NAME", "recipe_chatbot"),
    }

def fix_js_syntax(js_str):
    js_str = re.sub(r'(?<!")(\$?\w+)\s*:', r'"\1":', js_str)
    return js_str

def execute_mongo_query(query_obj):
    if isinstance(query_obj, str):
        query_obj = json.loads(query_obj)
    
    collection_name = query_obj.get("collection")
    query_filter = query_obj.get("query", {})
    limit = query_obj.get("limit", 10)

    config = load_config()
    db = MongoClient(config["MONGODB_URI"])[config["DB_NAME"]]
    collection = db[collection_name]

    print(f"⚙️ Executing query on `{collection_name}` with filter {query_filter} and limit {limit}")
    
    cursor = collection.find(query_filter)
    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)
