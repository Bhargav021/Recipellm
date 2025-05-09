#!/bin/bash

echo "Starting RecipeLLM application..."

# Check if MongoDB is running
if pgrep mongod > /dev/null
then
    echo "MongoDB is running ✅"
else
    echo "MongoDB is not running. Starting MongoDB..."
    mongod --fork --logpath /tmp/mongodb.log
    if [ $? -eq 0 ]; then
        echo "MongoDB started ✅"
    else
        echo "Failed to start MongoDB. Please start it manually."
        exit 1
    fi
fi

# Import data if needed
echo "Checking if data import is needed..."
python3 -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017/')['recipe_chatbot']['recipes'].count_documents({}))" > /tmp/count.txt
COUNT=$(cat /tmp/count.txt)
if [ "$COUNT" -eq "0" ] || [ "$COUNT" = "0" ]; then
    echo "No recipes found in database. Importing sample data..."
    python3 import_csv_to_mongodb.py
    echo "Data import complete ✅"
else
    echo "Database already contains $COUNT recipes ✅"
fi

# Start backend in a new terminal
echo "Starting Flask backend..."
osascript -e 'tell app "Terminal" to do script "cd '$PWD' && python3 app.py"'

# Start frontend in a new terminal
echo "Starting React frontend..."
osascript -e 'tell app "Terminal" to do script "cd '$PWD' && pnpm run dev"'

echo "RecipeLLM is starting up! The frontend should be available at http://localhost:5173" 