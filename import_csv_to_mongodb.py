import pandas as pd
from pymongo import MongoClient
import os

# MongoDB connection
def import_data():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['recipe_chatbot']
    collection = db['recipes']
    
    # Check if collection already has data to avoid duplicates
    if collection.count_documents({}) > 0:
        print("Data already exists in the collection. Skipping import.")
        return
    
    # Import CSV file
    print("Importing CSV data to MongoDB...")
    df = pd.read_csv('sample_food_com_recipes.csv')
    
    # Clean and prepare data
    # Convert DataFrame to list of dictionaries (MongoDB documents)
    records = df.to_dict('records')
    
    # Insert data into MongoDB
    if records:
        collection.insert_many(records)
        print(f"Successfully imported {len(records)} records to MongoDB")
    else:
        print("No records to import")

if __name__ == "__main__":
    import_data() 