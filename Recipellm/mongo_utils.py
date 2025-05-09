from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json

def load_config():
    """Load configuration from .env file or return default values"""
    load_dotenv()
    return {
        "API_KEY": os.getenv("LLM_API_KEY", ""),
        "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        "DB_NAME": os.getenv("DB_NAME", "recipe_chatbot")
    }

def connect_mongo():
    """Connect to MongoDB and return database instance"""
    config = load_config()
    client = MongoClient(config["MONGODB_URI"])
    return client[config["DB_NAME"]]

def execute_mongo_query(query_string):
    """Execute a MongoDB query
    This is a simplified version for the agent to use
    """
    try:
        db = connect_mongo()
        # Parse the query string - in a real app you'd want more validation
        query_parts = query_string.strip().split(' ')
        
        if len(query_parts) < 2:
            return {"error": "Invalid query"}
            
        collection_name = query_parts[0]
        operation = query_parts[1].lower()
        
        if collection_name not in db.list_collection_names():
            return {"error": f"Collection {collection_name} does not exist"}
            
        collection = db[collection_name]
        
        if operation == "find":
            # Extract query criteria if provided
            query = {}
            if len(query_parts) > 2:
                query_json = ' '.join(query_parts[2:])
                query = json.loads(query_json)
            
            # Execute find and return results
            results = list(collection.find(query).limit(10))
            
            # Convert ObjectId to string
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
                    
            return results
            
        elif operation == "count":
            return {"count": collection.count_documents({})}
            
        else:
            return {"error": f"Unsupported operation: {operation}"}
    
    except Exception as e:
        return {"error": str(e)} 