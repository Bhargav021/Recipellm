# agent3_sql_final.py — Fully mirrored from MongoDB agent3.py for PostgreSQL
from llm_sql_agent.db_utils import execute_sql_query, get_db_connection, load_config
from llm_sql_agent.llm_wrapper import Custom_GenAI
from llm_sql_agent.log_utils import insert_log
from llm_sql_agent.helper import get_country_iso3
from llm_sql_agent.utils import clean_sql_query, format_sql_results
import re
from datetime import datetime

PRIMARY_LLM = Custom_GenAI(load_config()["API_KEY"])
SYNTAX_LLM = Custom_GenAI(load_config()["API_KEY"])
query_cache = {}


def get_valid_fields(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {table_name} LIMIT 1")
        return [desc[0] for desc in cur.description]
    except:
        return []
    finally:
        cur.close()
        conn.close()

def list_all_tables_and_fields():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [row[0] for row in cur.fetchall()]
    result = []
    for table in tables:
        try:
            cur.execute(f"SELECT * FROM {table} LIMIT 1")
            fields = [desc[0] for desc in cur.description]
            result.append(f"📘 Table: `{table}`\nFields: {', '.join(fields)}")
        except:
            result.append(f"📘 Table: `{table}` (unable to fetch fields)")
    cur.close()
    conn.close()
    return "\n\n".join(result)

def preview_table(table):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {table} LIMIT 1")
        row = cur.fetchone()
        if row:
            fields = [desc[0] for desc in cur.description]
            return f"📘 Table: `{table}`\nFields: {', '.join(fields)}"
        else:
            return f"📘 Table: `{table}` (no sample found)"
    except Exception as e:
        return f"⚠️ Error previewing table `{table}`: {e}"
    finally:
        cur.close()
        conn.close()

def preprocess_country_names(query):
    words = query.split()
    for word in words:
        iso = get_country_iso3(word)
        if iso:
            query = re.sub(rf"\b{word}\b", iso, query, flags=re.IGNORECASE)
    return query

def run_sql_interactively(sql, table, action, user_query):
    if input("Run? (yes/no): ").lower() == "yes":
        try:
            _, _ = execute_sql_query(sql)
            insert_log(user_query, action, sql, table, success=True)
            return f"✅ {action} succeeded."
        except Exception as e:
            insert_log(user_query, action, sql, table, success=False)
            return f"❌ {action} failed: {e}"
    return f"{action} canceled."

# Manual CRUD Functions for all 3 tables
def add_recipe(_):
    name = input("🍽️ Recipe name: ")
    recipe_id = name.lower().replace(" ", "_")
    category = input("📂 Category: ")
    ingredients = input("🧂 Ingredients (comma-separated): ").split(",")
    calories = input("🔥 Calories: ")
    fat = input("🥓 Fat: ")
    carbs = input("🍞 Carbs: ")
    protein = input("🍗 Protein: ")
    instructions = input("📋 Instructions: ")
    sql = f"""INSERT INTO recipes (recipeid, name, recipeingredientparts, recipecategory, calories, fatcontent, carbohydratecontent, proteincontent, recipeinstructions, aggregatedrating, reviewcount)
              VALUES ({recipe_id!r}, {name!r}, ARRAY{ingredients!r}, {category!r}, {calories}, {fat}, {carbs}, {protein}, ARRAY[{instructions!r}], NULL, 0);"""
    print(sql)
    return run_sql_interactively(sql, "recipes", "INSERT", _)

def update_recipe(_):
    rid = input("🆔 Recipe ID: ")
    field = input("✏️ Field to update: ")
    val = input("New value: ")
    sql = f"UPDATE recipes SET {field} = {val!r} WHERE recipeid = {rid!r};"
    print(sql)
    return run_sql_interactively(sql, "recipes", "UPDATE", _)

def delete_recipe(user_query):
    return {
        "action": "collect_input",
        "operation": "delete",
        "table": "recipes",
        "fields": [
            {
                "name": "recipeid",
                "type": "string",  # or "integer" if you're strict
                "required": True,
                "description": "ID of the recipe to delete"
            }
        ],
        "original_query": user_query
    }


def add_nutrition(_):
    name = input("🥦 Ingredient name: ")
    cat = input("📂 Category: ")
    kcal = input("🔥 Energy kcal: ")
    fat = input("🥓 Fat: ")
    carbs = input("🍞 Carbs: ")
    prot = input("🍗 Protein: ")
    sql = f"""INSERT INTO ingredient_nutrition (ingredient_name, category_name, fat_g, carbohydrate_g, protein_g, energy_kcal)
              VALUES ({name!r}, {cat!r}, {fat}, {carbs}, {prot}, {kcal});"""
    print(sql)
    return run_sql_interactively(sql, "ingredient_nutrition", "INSERT", _)

def update_nutrition(_):
    ing = input("🥦 Ingredient name: ")
    field = input("✏️ Field to update: ")
    val = input("New value: ")
    sql = f"UPDATE ingredient_nutrition SET {field} = {val} WHERE ingredient_name = {ing!r};"
    print(sql)
    return run_sql_interactively(sql, "ingredient_nutrition", "UPDATE", _)

def delete_nutrition(_):
    ing = input("🥦 Ingredient name: ")
    sql = f"DELETE FROM ingredient_nutrition WHERE ingredient_name = {ing!r};"
    print(sql)
    return run_sql_interactively(sql, "ingredient_nutrition", "DELETE", _)

def add_price(_):
    iso = input("🌍 Country ISO3: ")
    date = input("📅 Date (YYYY-MM-DD): ")
    market = input("🏪 Market: ")
    cat = input("📂 Category: ")
    com = input("🥦 Commodity: ")
    unit = input("⚖️ Unit: ")
    price = input("💰 Price: ")
    usd = input("💵 USD: ")
    sql = f"""INSERT INTO food_prices (countryiso3, date, market, category, commodity, unit, price, usdprice)
              VALUES ({iso!r}, {date!r}, {market!r}, {cat!r}, {com!r}, {unit!r}, {price}, {usd});"""
    print(sql)
    return run_sql_interactively(sql, "food_prices", "INSERT", _)

def update_price(_):
    com = input("🥦 Commodity: ")
    field = input("✏️ Field: ")
    val = input("New value: ")
    sql = f"UPDATE food_prices SET {field} = {val} WHERE commodity = {com!r};"
    print(sql)
    return run_sql_interactively(sql, "food_prices", "UPDATE", _)

def delete_price(_):
    com = input("🥦 Commodity: ")
    sql = f"DELETE FROM food_prices WHERE commodity = {com!r};"
    print(sql)
    return run_sql_interactively(sql, "food_prices", "DELETE", _)

def process_query(user_query):

    if "=" in user_query and "," in user_query:
        try:
            structured_input = {}
            parts = [p.strip() for p in user_query.split(",")]

            # Rebuild the key=value list correctly
            temp = []
            i = 0
            while i < len(parts):
                if "=" in parts[i]:
                    key, value = parts[i].split("=", 1)
                    while i + 1 < len(parts) and "=" not in parts[i + 1]:
                        value += f", {parts[i + 1]}"
                        i += 1
                    temp.append((key.strip(), value.strip()))
                i += 1

            structured_input = dict(temp)

            op = query_cache.get("pending_op", {})
            table = op.get("table")
            action = op.get("operation")

            if not table or not action:
                return "⚠️ No operation context. Try again."

            if action == "insert":
                fields = []
                values = []

                for k, v in structured_input.items():
                    fields.append(k)

                    # Normalize array fields
                    if k in ["recipeingredientparts"]:
                        array_values = [f"'{i.strip()}'" for i in v.split(",")]
                        values.append(f"ARRAY[{', '.join(array_values)}]")

                    # Normalize date fields
                    elif k in ["date"]:
                        values.append(f"DATE '{v}'")

                    # Use numeric as-is, else wrap in quotes
                    elif v.replace('.', '', 1).isdigit():
                        values.append(v)
                    else:
                        values.append(f"'{v}'")

                sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(values)});"


            elif action == "update":
                field = structured_input.get("field")
                value = structured_input.get("value")
                if not field or not value:
                    return "❌ Update must include field and value."
                if table == "recipes":
                    filter_expr = f"recipeid = '{structured_input.get('recipeid', '')}'"
                elif table == "ingredient_nutrition":
                    filter_expr = f"ingredient_name = '{structured_input.get('ingredient_name', '')}'"
                elif table == "food_prices":
                    filter_expr = f"commodity = '{structured_input.get('commodity', '')}'"
                else:
                    return "❌ Table not supported."
                sql = f"UPDATE {table} SET {field} = '{value}' WHERE {filter_expr};"

            elif action == "delete":
                if table == "recipes":
                    sql = f"DELETE FROM recipes WHERE recipeid = '{structured_input.get('recipeid', '')}';"
                elif table == "ingredient_nutrition":
                    sql = f"DELETE FROM ingredient_nutrition WHERE ingredient_name = '{structured_input.get('ingredient_name', '')}';"
                elif table == "food_prices":
                    sql = f"DELETE FROM food_prices WHERE commodity = '{structured_input.get('commodity', '')}' AND market = '{structured_input.get('market', '')}';"
                else:
                    return "❌ Delete unsupported for this table."

            rows, cols = execute_sql_query(sql)
            insert_log(user_query, action.upper(), sql, table, success=True)
            return f"✅ {action.title()} on {table} successful."

        except Exception as e:
            return f"❌ Failed to parse structured input: {e}"



    user_query = preprocess_country_names(user_query)
    uq = user_query.lower().strip()

    if any(k in uq for k in ["list tables", "show tables", "available tables", "schema"]):
        return list_all_tables_and_fields()
    if match := re.search(r"(?:fields|attributes|schema) of (\w+)", uq):
        return preview_table(match.group(1))
    
    # Handle frontend response to confirmation
    if uq in ["yes", "no", "rewrite"]:
        if uq == "no":
            insert_log("Query canceled", "CANCEL", query_cache.get("pending_sql", ""), success=False)
            return "❌ Query canceled."
        elif uq == "rewrite":
            return {
                "action": "request_rewrite",
                "prompt": "🔁 Please clarify your question:"
            }
        elif uq == "yes":
            cleaned_sql = query_cache.pop("pending_sql", "")
            try:
                rows, cols = execute_sql_query(cleaned_sql)
                insert_log(user_query, "QUERY", cleaned_sql, success=bool(rows))
                return format_sql_results(rows, cols) if rows else "❗ No results."
            except Exception as e:
                insert_log(user_query, "ERROR", cleaned_sql, success=False)
                return f"❌ SQL Execution Error: {e}"


    if "add recipe" in uq:
        query_cache["pending_op"] = {"table": "recipes", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "table": "recipes",
            "fields": [
                "recipeid", "name", "recipeingredientparts", "recipecategory",
                "calories", "fatcontent", "carbohydratecontent",
                "proteincontent", "recipeinstructions"
            ],
            "prompt": "📝 Please enter: recipeid, name, ingredients (comma-separated), and nutrition values."
        }

    if "update recipe" in uq or "modify recipe" in uq:
        query_cache["pending_op"] = {"table": "recipes", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "table": "recipes",
            "fields": ["recipeid", "field", "value"],
            "prompt": "✏️ Enter: recipeid, field to update, and new value."
        }

    if "delete recipe" in uq or "remove recipe" in uq:
        query_cache["pending_op"] = {"table": "recipes", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "table": "recipes",
            "fields": ["recipeid"],
            "prompt": "🗑️ Enter the recipeid to delete."
        }

    if "add nutrition" in uq:
        query_cache["pending_op"] = {"table": "ingredient_nutrition", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "table": "ingredient_nutrition",
            "fields": [
                "ingredient_name", "category_name", "fat_g",
                "carbohydrate_g", "protein_g", "energy_kcal"
            ],
            "prompt": "📝 Enter: ingredient name, category, and basic nutrition info."
        }

    if "update nutrition" in uq or "modify nutrition" in uq:
        query_cache["pending_op"] = {"table": "ingredient_nutrition", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "table": "ingredient_nutrition",
            "fields": ["ingredient_name", "field", "value"],
            "prompt": "✏️ Enter: ingredient name, field to update, and new value."
        }

    if "delete nutrition" in uq or "remove nutrition" in uq:
        query_cache["pending_op"] = {"table": "ingredient_nutrition", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "table": "ingredient_nutrition",
            "fields": ["ingredient_name"],
            "prompt": "🗑️ Enter the ingredient name to delete."
        }

    if "add price" in uq:
        query_cache["pending_op"] = {"table": "food_prices", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "table": "food_prices",
            "fields": [
                "countryiso3", "date", "market", "category", "commodity",
                "unit", "price", "usdprice"
            ],
            "prompt": "📝 Enter all details: ISO3, date, market, commodity, price, etc."
        }

    if "update price" in uq or "modify price" in uq:
        query_cache["pending_op"] = {"table": "food_prices", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "table": "food_prices",
            "fields": ["commodity", "market", "field", "value"],
            "prompt": "✏️ Enter: commodity, market, field to update, and new value."
        }

    if "delete price" in uq or "remove price" in uq:
        query_cache["pending_op"] = {"table": "food_prices", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "table": "food_prices",
            "fields": ["commodity", "market"],
            "prompt": "🗑️ Enter: commodity and market to delete."
        }


    with open("llm_sql_agent/db_schema_context.sql", "r") as schema_file:
        schema = schema_file.read()
    with open("llm_sql_agent/llm_prompt.txt", "r") as prompt_file:
        prompt = prompt_file.read()
    final_prompt = prompt.replace("{SCHEMA}", schema).replace("{QUESTION}", user_query)
    raw_sql = PRIMARY_LLM.ask_ai(final_prompt)
    cleaned_sql = clean_sql_query(raw_sql)
    print("\n🧠 Generated SQL Query:\n", cleaned_sql)

    with open("llm_sql_agent/db_schema_context.sql", "r", encoding="utf-8") as schema_file:
        sql_schema_context = schema_file.read()

    syntax_prompt = f"""You are a PostgreSQL syntax and schema validator.

        Below is the database schema:
        {sql_schema_context}

        And here is the generated SQL query:
        {cleaned_sql}

        Please check if:
        - The syntax is valid
        - All table and column names match the schema
        - The joins and field references are valid
        NOTE: food_prices does NOT contain fdc_id. It should be joined via recipe_ingredients.fdc_id.

        If something is wrong, suggest the corrected version.
        If valid, reply with 'Valid ✅'.  
        If invalid, reply only with the corrected SQL query enclosed in a ```sql block — and nothing else.

        """
    feedback = SYNTAX_LLM.ask_ai(syntax_prompt)
    print("\n🧪 Syntax LLM Feedback:\n", feedback)
    if "Valid ✅" not in feedback and any(kw in feedback for kw in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
        cleaned_sql = clean_sql_query(feedback)
        print("\n✅ Using corrected SQL:\n", cleaned_sql)

        query_cache["pending_sql"] = cleaned_sql  # store for later execution
        return {
            "action": "confirm_query",
            "query": cleaned_sql,
            "prompt": "⚠️ Should I run this query?\nReply with: yes / no / rewrite"
        }


    try:
        rows, cols = execute_sql_query(cleaned_sql)
        insert_log(user_query, "QUERY", cleaned_sql, success=bool(rows))
        return format_sql_results(rows, cols) if rows else "❗ No results."
    except Exception as e:
        insert_log(user_query, "ERROR", cleaned_sql, success=False)
        return f"❌ SQL Execution Error: {e}"

if __name__ == "__main__":
    print("🧠 Welcome to your LLM-powered PostgreSQL Assistant.")
    print("Type 'exit' or 'quit' to leave.\n")
    while True:
        user_input = input("🧑‍🍳 Ask your database a question: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
        print("\n📋 Response:\n", process_query(user_input))
        print("\n" + "=" * 60 + "\n")
