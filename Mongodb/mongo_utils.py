from pymongo import MongoClient
import json
import re

client = MongoClient("mongodb://localhost:27017/")
db = client["recipe_chatbot"]

def connect_mongo():
    return db

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def fix_js_syntax(js_str):
    js_str = re.sub(r'(?<!")(\$?\w+)\s*:', r'"\1":', js_str)
    return js_str

def execute_mongo_query(query_string_or_dict):
    if isinstance(query_string_or_dict, str):
        try:
            query_dict = json.loads(query_string_or_dict)
        except Exception as e:
            raise ValueError(f"Invalid query string JSON: {e}")
    else:
        query_dict = query_string_or_dict

    collection = query_dict["collection"]
    query = query_dict["query"]

    return list(db[collection].find(query))
