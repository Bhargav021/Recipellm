from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from SQL.db_utils import execute_sql_query
from SQL.log_utils import insert_log
from Mongodb.agent3 import process_query as process_mongo
from SQL.agent3_sql_final import process_query as process_sql
from Mongodb.mongo_utils import load_config as load_mongo_config
from SQL.db_utils import load_config as load_sql_config

app = Flask(__name__)
CORS(app)

# Load config (API key, DB password)
mongo_config = load_mongo_config()
sql_config = load_sql_config()

@app.route("/health")
def health():
    return jsonify({"status": "up"})

@app.route("/")
def home():
    return "👋 Welcome to RecipeLLM Backend (Hybrid Mongo + SQL)!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_query = data.get("query", "")
        mode = data.get("mode", "mongo").lower().strip()  # Default to Mongo

        if not user_query:
            return jsonify({"error": "Query is required."}), 400

        print(f"\n🧠 User query: {user_query}")
        print(f"🧭 Mode selected: {mode}")

        if mode == "mongo":
            result = process_mongo(user_query)
        elif mode == "sql":
            result = process_sql(user_query)
        else:
            return jsonify({"error": "Invalid mode. Use 'mongo' or 'sql'."}), 400

        # Handle return type: dict (action) vs string (result)
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"result": result})

    except Exception as e:
        print(f"❌ Backend error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    action = data.get("operation")
    table = data.get("table")
    fields = data.get("fields", {})
    user_query = data.get("original_query", "")
    mode = data.get("mode", "sql")  # default to SQL if not passed

    try:
        # ---------------------- DELETE ----------------------
        if action == "delete":
            if table == "recipes":
                key = "recipeid" if mode == "sql" else "name"
                val = fields.get(key)
                if not val:
                    return jsonify({"error": f"Missing required key: {key}"}), 400
                sql = f"DELETE FROM recipes WHERE {key} = {val!r};"

            elif table == "ingredient_nutrition":
                key = "ingredient_name"
                val = fields.get(key)
                sql = f"DELETE FROM ingredient_nutrition WHERE {key} = {val!r};"

            elif table == "food_prices":
                com = fields.get("commodity")
                market = fields.get("market")
                sql = f"DELETE FROM food_prices WHERE commodity = {com!r} AND market = {market!r};"

            _, _ = execute_sql_query(sql)
            insert_log(user_query, "DELETE", sql, table, success=True)
            return jsonify({"result": f"🗑️ Deleted entry from {table}."})

        # ---------------------- UPDATE ----------------------
        elif action == "update":
            field = fields.get("field")
            value = fields.get("value")
            if not field or value is None:
                return jsonify({"error": "❌ 'field' and 'value' are required for update."}), 400

            if table == "recipes":
                key = "recipeid" if mode == "sql" else "name"
                val = fields.get(key)
                sql = f"UPDATE recipes SET {field} = {value!r} WHERE {key} = {val!r};"

            elif table == "ingredient_nutrition":
                key = "ingredient_name"
                val = fields.get(key)
                sql = f"UPDATE ingredient_nutrition SET {field} = {value!r} WHERE {key} = {val!r};"

            elif table == "food_prices":
                com = fields.get("commodity")
                market = fields.get("market")
                sql = f"UPDATE food_prices SET {field} = {value!r} WHERE commodity = {com!r} AND market = {market!r};"

            _, _ = execute_sql_query(sql)
            insert_log(user_query, "UPDATE", sql, table, success=True)
            return jsonify({"result": f"✏️ Updated {field} in {table}."})

        # ---------------------- INSERT ----------------------
        elif action == "insert":
            if table == "recipes":
                if mode == "sql":
                    required = ["recipeid", "name", "recipeingredientparts", "recipecategory",
                                "calories", "fatcontent", "carbohydratecontent", "proteincontent", "recipeinstructions"]
                else:  # mongo
                    required = ["name", "recipecategory", "recipeingredientparts",
                                "calories", "fatcontent", "carbohydratecontent", "proteincontent", "recipeinstructions"]

                arr_parts = ', '.join(f"'{i.strip()}'" for i in (fields.get("recipeingredientparts") or "").split(","))
                arr_instr = ', '.join(f"'{i.strip()}'" for i in (fields.get("recipeinstructions") or "").split(","))

                rid_expr = f"{fields['recipeid']!r}," if mode == "sql" else ""
                col_expr = f"recipeid, " if mode == "sql" else ""

                sql = f"""INSERT INTO recipes ({col_expr}name, recipeingredientparts, recipecategory,
                          calories, fatcontent, carbohydratecontent, proteincontent, recipeinstructions)
                          VALUES ({rid_expr}{fields['name']!r}, ARRAY[{arr_parts}],
                          {fields['recipecategory']!r}, {fields['calories']}, {fields['fatcontent']},
                          {fields['carbohydratecontent']}, {fields['proteincontent']}, ARRAY[{arr_instr}]);"""

            elif table == "ingredient_nutrition":
                sql = f"""INSERT INTO ingredient_nutrition (ingredient_name, category_name, fat_g,
                          carbohydrate_g, protein_g, energy_kcal)
                          VALUES ({fields['ingredient_name']!r}, {fields['category_name']!r}, {fields['fat_g']},
                          {fields['carbohydrate_g']}, {fields['protein_g']}, {fields['energy_kcal']});"""

            elif table == "food_prices":
                sql = f"""INSERT INTO food_prices (countryiso3, date, market, category, commodity,
                          unit, price, usdprice)
                          VALUES ({fields['countryiso3']!r}, DATE {fields['date']!r}, {fields['market']!r},
                          {fields['category']!r}, {fields['commodity']!r}, {fields['unit']!r},
                          {fields['price']}, {fields['usdprice']});"""

            _, _ = execute_sql_query(sql)
            insert_log(user_query, "INSERT", sql, table, success=True)
            return jsonify({"result": f"✅ Inserted into {table} successfully."})

        else:
            return jsonify({"error": f"❌ Unknown action: {action}"}), 400

    except Exception as e:
        print("❌ SUBMIT ERROR:", e)
        return jsonify({"error": f"❌ Submit failed: {e}"}), 500






if __name__ == "__main__":
    app.run(port=5001, debug=True)
