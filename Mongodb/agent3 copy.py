# llm_agent_mongo.py (Full CRUD with Flexible Matching & Input Validation)
#create table script addition
#create app.py for the script
from Mongodb.mongo_utils import execute_mongo_query, connect_mongo, load_config
from Mongodb.llm_wrapper import Custom_GenAI
from pymongo import MongoClient
from Mongodb.log_utils_mongo import insert_log
from Mongodb.utils import clean_query, format_mongo_results, extract_json_block
import json
from datetime import datetime
import re
from bson import ObjectId

PRIMARY_LLM = Custom_GenAI(load_config()["API_KEY"])
SYNTAX_LLM = Custom_GenAI(load_config()["API_KEY"])

query_cache = {}


field_defaults = {
    "recipes": [
        "name", "recipecategory", "recipeingredientparts", "calories",
        "fatcontent", "carbohydratecontent", "proteincontent", "recipeinstructions",
        "aggregatedrating", "reviewcount"
    ],
    "ingredient_nutrition": [
        "fdc_id", "ingredient_name", "food_category_id", "category_name",
        "portion_description", "gram_weight", "calcium_mg", "carbohydrate_g",
        "energy_kcal", "energy_kj", "fiber_g", "folate_ug", "iron_mg",
        "magnesium_mg", "potassium_mg", "protein_g", "sodium_mg", "fat_g",
        "vitamin_a_rae_ug", "vitamin_b12_ug", "vitamin_c_ascorbic_ug",
        "vitamin_d_ug", "zinc_mg"
    ],
    "food_prices": [
        "countryiso3", "date", "market", "category", "commodity",
        "unit", "price", "usdprice"
    ]
}


def get_valid_fields(collection_name):
    db = MongoClient("mongodb://localhost:27017/")["recipe_chatbot"]
    sample_doc = db[collection_name].find_one()
    default_fields = set(field_defaults.get(collection_name, []))
    if sample_doc:
        # Combine actual keys + backup defaults to avoid missing anything
        actual_fields = set(sample_doc.keys())
        return actual_fields | default_fields  # union
    
    else:
        return default_fields
   

def match_intent(uq, keywords):
    return all(k in uq for k in keywords)

def safe_preview(doc):
    if not doc:
        return {}
    cleaned = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            cleaned[k] = str(v)
        elif isinstance(v, datetime):
            cleaned[k] = v.strftime("%Y-%m-%d")
        else:
            cleaned[k] = v
    return cleaned


def safe_float(prompt):
    while True:
        val = input(prompt)
        if val == "":
            return None
        try:
            return float(val)
        except ValueError:
            print("❗ Please enter a valid number.")

def safe_date(prompt):
    val = input(prompt)
    if val == "":
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        print("❗ Please enter a valid date in YYYY-MM-DD format.")
        return safe_date(prompt)

def preview_doc(doc):
    return {
        k: (v.strftime("%Y-%m-%d") if isinstance(v, datetime) else v)
        for k, v in doc.items()
    }

def parse_date_safe(val):
    try:
        return datetime.strptime(val, "%Y-%m-%d")
    except:
        return val


def process_query(user_query):

    # Step 0: Handle structured form input like: name=abc, fat_g=5 ...
    if "=" in user_query:
        try:
            # Split correctly even if no commas (safe fallback for space-separated key=val too)
            parts = re.findall(r'(\w+)=(".*?"|\'.*?\'|[^,]+)', user_query)

            # 👇 If no valid key=value pairs found, stop and fallback
            if not parts:
                return "❌ Could not parse structured input. Please use key=value format."

            structured_input = {}
            for key, val in parts:
                key = key.strip()
                val = val.strip().strip('"').strip("'")

                # Normalize array fields like ingredients
                if key in ["recipe_ingredient_parts"]:
                    # Allow comma-separated or single entry
                    structured_input[key] = [v.strip().strip('"').strip("'") for v in val.split(",")]

                elif key in ["date"]:
                    structured_input[key] = parse_date_safe(val)

                elif val == "":
                    structured_input[key] = None  # Treat empty values as NULLs

                else:
                    structured_input[key] = val

            # ✅ Check operation context (prevents fallback to LLM)
            op_info = query_cache.get("pending_op", {})
            collection = op_info.get("collection")
            operation = op_info.get("operation")

            if not collection or not operation:
                return "⚠️ Operation context missing. Please retry your request."



            db = connect_mongo()

            # ----------------- INSERT -----------------
            if operation == "insert":
                print(json.dumps(structured_input, indent=2))
                result = db[collection].insert_one(structured_input)
                inserted = db[collection].find_one({"_id": result.inserted_id})
                preview = safe_preview(inserted)
                insert_log(user_query, "INSERT", json.dumps(preview), success=True)
                return f"<b>✅ {collection.title()} inserted:</b><br>{json.dumps(preview, indent=2)}"


            # ----------------- UPDATE -----------------
            elif operation == "update":
                field = structured_input.get("field")
                value = structured_input.get("value")

                if not field or value is None:
                    return "❌ 'field' and 'value' required for update."

                if collection == "recipes" and "name" in structured_input:
                    match_filter = {"name": structured_input["name"]}
                elif collection == "food_prices" and "commodity" in structured_input and "market" in structured_input:
                    match_filter = {"commodity": structured_input["commodity"], "market": structured_input["market"]}
                elif collection == "ingredient_nutrition" and "ingredient_name" in structured_input:
                    match_filter = {"ingredient_name": structured_input["ingredient_name"]}
                else:
                    return "❌ Not enough keys to identify the document."

                # Convert numeric if applicable
                try:
                    value = float(value) if value.replace(".", "", 1).isdigit() else value
                except:
                    pass

                update_result = db[collection].update_one(match_filter, {"$set": {field: value}})
                if update_result.modified_count:
                    insert_log(user_query, "UPDATE", f"{match_filter} => {field} = {value}", success=True)
                    return f"<b>✅ Updated</b> {field} in {collection}."
                else:
                    return "⚠️ No changes made (maybe value was identical)."

            # ----------------- DELETE -----------------
            elif operation == "delete":
                if collection == "recipes" and "name" in structured_input:
                    filter_query = {"name": structured_input["name"]}
                elif collection == "food_prices" and "commodity" in structured_input and "market" in structured_input:
                    filter_query = {"commodity": structured_input["commodity"], "market": structured_input["market"]}
                elif collection == "ingredient_nutrition" and "ingredient_name" in structured_input:
                    filter_query = {"ingredient_name": structured_input["ingredient_name"]}
                else:
                    return "❌ Not enough data to perform delete."

                delete_result = db[collection].delete_one(filter_query)
                if delete_result.deleted_count:
                    insert_log(user_query, "DELETE", f"{filter_query}", success=True)
                    return f"<b>🗑️ Deleted entry from {collection}.</b>"
                else:
                    return "⚠️ No matching entry found to delete."

            else:
                return f"❌ Unsupported operation type: {operation}"

        except Exception as e:
            return f"❌ Failed to process structured input: {e}"

        

    db = connect_mongo()
    uq = user_query.lower().strip()
    wrapped_query = None
    cleaned_query = ""  # Optional: can update later

    # Step 1: Handle responses from previous interaction
    if uq in ["yes", "no", "rewrite"]:
        if uq == "no":
            insert_log("Query canceled", "CANCEL", cleaned_query, success=False)
            return "❌ Query execution canceled."
        elif uq == "rewrite":
            return {
                "action": "request_rewrite",
                "prompt": "🔁 Please clarify your question:"
            }
        elif uq == "yes":
            if "pending" in query_cache:
                wrapped_query = query_cache.pop("pending")  # 💾 Load and clear cache
                try:
                    result = execute_mongo_query(db, wrapped_query)
                    insert_log(user_query, "EXECUTE", wrapped_query, success=True, matched=len(result))
                    return result
                except Exception as e:
                    return f"❌ Failed to execute query: {e}"
            else:
                return "⚠️ No query to execute."
    
    introspect_keywords = ["table", "tables", "collection", "collections"]
    list_keywords = ["what", "list", "show", "see", "available"]

    print(f"🔍 Interpreted user query: '{uq}'")
    print(f"🔍 Trigger introspection? {any(k1 in uq for k1 in introspect_keywords)} and {any(k2 in uq for k2 in list_keywords)}")

    if any(k1 in uq for k1 in introspect_keywords) and any(k2 in uq for k2 in list_keywords):
        collections = db.list_collection_names()

        # Check if user mentions a specific table name (like recipe/recipes)
        uq_clean = uq.replace("table", "").replace("collection", "").strip()
        for coll in collections:
            if coll in uq_clean or coll.rstrip("s") in uq_clean or uq_clean.rstrip("s") == coll:
                sample = db[coll].find_one()
                if sample:
                    fields = list(sample.keys())
                    return f"📘 Collection: `{coll}`\nFields: {', '.join(fields)}"
                else:
                    return f"📘 Collection: `{coll}` (no sample found)"
        
        # If no specific table mentioned, show all collections
        result = []
        for coll in collections:
            sample = db[coll].find_one()
            if sample:
                fields = list(sample.keys())
                result.append(f"📘 Collection: `{coll}`\nFields: {', '.join(fields)}")
            else:
                result.append(f"📘 Collection: `{coll}` (no sample found)")
        return "\n\n".join(result)




    # # ---------------------- schema of db ----------------------
    # if match_intent(uq, ["tables"]) or match_intent(uq, ["list", "collections"]):
    #     collections = db.list_collection_names()
    #     result = []

    #     for coll in collections:
    #         sample = db[coll].find_one()
    #         if sample:
    #             fields = list(sample.keys())
    #             result.append(f"📘 Collection: `{coll}`\nFields: {', '.join(fields)}")
    #         else:
    #             result.append(f"📘 Collection: `{coll}` (no sample found)")

    #     return "\n\n".join(result)




     # ---------------------- INSERT ----------------------
    elif match_intent(uq, ["add", "recipe"]) or match_intent(uq, ["insert", "recipe"]):
        expected_fields = [
            "name", "recipe_category", "recipe_ingredient_parts", "calories", "fat_g",
            "carbohydrate_g", "protein_g", "recipe_instructions"
        ]
        query_cache["pending_op"] = {"collection": "recipes", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "collection": "recipes",
            "fields": expected_fields,
            "prompt": f"📝 Please enter values for: {', '.join(expected_fields)}"
        }



#######insert price
    elif match_intent(uq, ["add", "price"]) or match_intent(uq, ["insert", "price"]):
        expected_fields = [
            "countryiso3", "date", "market", "category", "commodity",
            "unit", "price", "usdprice"
        ]
        query_cache["pending_op"] = {"collection": "food_prices", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "collection": "food_prices",
            "fields": expected_fields,
            "prompt": f"📝 Please enter values for: {', '.join(expected_fields)}"
        }




#######insert nutrition
    elif match_intent(uq, ["add", "nutrition"]) or match_intent(uq, ["insert", "nutrition"]):
        print("\n🔧 Let's collect the nutrition information.")
        expected_fields = [
            "ingredient_name", "food_category_id", "category_name", "portion_description",
            "gram_weight", "protein_g", "fat_g", "carbohydrate_g"
        ]
        query_cache["pending_op"] = {"collection": "ingredient_nutrition", "operation": "insert"}
        return {
            "action": "collect_input",
            "operation": "insert",
            "collection": "ingredient_nutrition",
            "fields": expected_fields,
            "prompt": f"📝 Please enter values for: {', '.join(expected_fields)}"
        }



    # ---------------------- UPDATE ----------------------
    #recipe
    elif match_intent(uq, ["modify", "recipe"]) or match_intent(uq, ["change", "recipe"]) or match_intent(uq, ["update", "recipe"]) or match_intent(uq, ["Update", "recipe"]):
        query_cache["pending_op"] = {"collection": "recipes", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "collection": "recipes",
            "fields": ["name", "field", "value"],
            "prompt": "📝 Please enter: recipe name, field to update, and the new value."
        }



#price
    elif match_intent(uq, ["modify", "price"]) or match_intent(uq, ["change", "price"]) or match_intent(uq, ["update", "price"]) or match_intent(uq, ["Update", "price"]):
        query_cache["pending_op"] = {"collection": "food_prices", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "collection": "food_prices",
            "fields": ["commodity", "market", "field", "value"],
            "prompt": "📝 Please enter: commodity, market, field to update, and the new value."
        }


#nutrition
    elif match_intent(uq, ["modify", "nutrition"]) or match_intent(uq, ["change", "nutrition"]) or match_intent(uq, ["update", "nutrition"]) or match_intent(uq, ["Update", "nutrition"]):
        query_cache["pending_op"] = {"collection": "ingredient_nutrition", "operation": "update"}
        return {
            "action": "collect_input",
            "operation": "update",
            "collection": "ingredient_nutrition",
            "fields": ["ingredient_name", "field", "value"],
            "prompt": "📝 Please enter: ingredient name, field to update, and the new value."
        }


    # ---------------------- DELETE ----------------------
    #recipe
    elif match_intent(uq, ["delete", "recipe"]) or match_intent(uq, ["remove", "recipe"]):
        query_cache["pending_op"] = {"collection": "recipes", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "collection": "recipes",
            "fields": ["name"],
            "prompt": "🗑️ Please enter the recipe name to delete:"
        }

    

#price
    elif match_intent(uq, ["delete", "price"]) or match_intent(uq, ["remove", "price"]):
        query_cache["pending_op"] = {"collection": "food_prices", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "collection": "food_prices",
            "fields": ["commodity", "market"],
            "prompt": "🗑️ Please enter: commodity and market to delete:"
        }



#nutrition
    elif match_intent(uq, ["delete", "nutrition"]) or match_intent(uq, ["remove", "nutrition"]):
        query_cache["pending_op"] = {"collection": "ingredient_nutrition", "operation": "delete"}
        return {
            "action": "collect_input",
            "operation": "delete",
            "collection": "ingredient_nutrition",
            "fields": ["ingredient_name"],
            "prompt": "🗑️ Please enter the ingredient name to delete:"
        }







    # LLM-based Search
    with open("Mongodb/db_schema_context_mongo.txt", "r") as schema_file:
        schema = schema_file.read()
    with open("Mongodb/llm_prompt_mongo.txt", "r", encoding='utf-8') as prompt_file:
        base_prompt = prompt_file.read()

    # user_query = user_query.replace("food_category_id", "").replace("category_name", "")
    final_prompt = base_prompt.replace("{SCHEMA}", schema).replace("{QUESTION}", user_query)
    raw_query = PRIMARY_LLM.ask_ai(final_prompt)

    # Step 1: Clean and extract
   # Clean raw query output
    # Clean raw query output
    raw_cleaned = clean_query(raw_query)

    # Remove JSON prefix if present
    if raw_cleaned.lower().startswith("json"):
        raw_cleaned = raw_cleaned[4:].strip()

    # Try extracting the first valid JSON object (handle LLM line breaks etc.)
    try:
        matches = re.findall(r'{[\s\S]+?}', raw_cleaned)
        for candidate in matches:
            try:
                parsed = json.loads(candidate)
                if "collection" in parsed and "query" in parsed:
                    query_cache["pending"] = parsed
                    return {
                        "action": "confirm_query",
                        "prompt": f"⚠️ Should I run this query on `{parsed.get('collection')}`?\nReply with: yes / no / rewrite"
                    }
            except Exception as e:
                continue  # skip invalid chunks
    except Exception as e:
        print(f"❌ Could not extract JSON from:\n{raw_cleaned}")

    # If nothing valid was parsed, fallback
    cleaned_query = raw_cleaned





    print("\n🧠 Generated Mongo Query (LLM):\n")
    print(cleaned_query)   

    if cleaned_query.strip().startswith("db.") or cleaned_query.strip().startswith("show"):
        try:
            if "list_collection_names" in cleaned_query:
                collections = db.list_collection_names()
                return "\n".join([f"📘 {c}" for c in collections])
            elif cleaned_query.startswith("show collections"):
                collections = db.list_collection_names()
                return "\n".join([f"📘 {c}" for c in collections])
            elif "find_one().keys()" in cleaned_query:
                coll_name = re.findall(r"db\.(\w+)\.find_one", cleaned_query)
                if coll_name:
                    sample = db[coll_name[0]].find_one()
                    if sample:
                        return f"🧾 Fields in `{coll_name[0]}`:\n" + ", ".join(sample.keys())
                    else:
                        return f"⚠️ No sample found in `{coll_name[0]}`"
        except Exception as e:
            return f"❌ Failed to run client command: {e}"
        
    # Clean and extract raw LLM output
    # Clean raw query output
    raw_cleaned = clean_query(raw_query)

    # Remove JSON prefix if present
    if raw_cleaned.lower().startswith("json"):
        raw_cleaned = raw_cleaned[4:].strip()

    # Try extracting the first valid JSON object (handle LLM line breaks etc.)
    try:
        matches = re.findall(r'{[\s\S]+?}', raw_cleaned)
        for candidate in matches:
            try:
                parsed = json.loads(candidate)
                if "collection" in parsed and "query" in parsed:
                    query_cache["pending"] = parsed
                    return {
                        "action": "confirm_query",
                        "prompt": f"⚠️ Should I run this query on `{parsed.get('collection')}`?\nReply with: yes / no / rewrite"
                    }
            except Exception as e:
                continue  # skip invalid chunks
    except Exception as e:
        print(f"❌ Could not extract JSON from:\n{raw_cleaned}")

    # If nothing valid was parsed, fallback
    cleaned_query = raw_cleaned

 

    print("\n🧠 Generated Mongo Query (LLM):\n")
    print(cleaned_query)

    with open("db_schema_context_mongo.txt", "r", encoding="utf-8") as schema_file:
        mongo_schema = schema_file.read()

    syntax_prompt = f"""You are an expert MongoDB syntax and schema validator.
    Below is the database schema:
    {mongo_schema}

    And here is the generated query:
    {cleaned_query}

    Please check if:
    - The syntax is valid
    - All field and collection names match the schema
    - The structure (e.g., pipeline stages) is correct

    If something is wrong, suggest the corrected version. Otherwise, reply 'Valid ✅'.
    """
    syntax_feedback = SYNTAX_LLM.ask_ai(syntax_prompt)
    print("\n🧪 Syntax LLM feedback:\n", syntax_feedback)

    # Check if the feedback includes a corrected query
    if "{" in syntax_feedback and "collection" in syntax_feedback and "query" in syntax_feedback:
        matches = re.findall(r'{[\s\S]+}', syntax_feedback)
        if matches:
            try:
                corrected_query = json.loads(matches[0])
                print("⚠️ Detected corrected query. Overriding previous query with this one:")
                print(json.dumps(corrected_query, indent=2))
                wrapped_query = corrected_query  # ✅ Assign corrected query
            except json.JSONDecodeError as e:
                print(f"❌ Could not parse corrected JSON: {e}")
                return f"<b>Failed to parse regenerated query: {e}</b>"  # ✅ Make sure to return here

        else:
            print("❌ No valid JSON query found in LLM feedback.")
            return "<b>Query could not be regenerated. Try rephrasing.</b>"  # ✅ Also return here

        # ✅ Final safety return if wrapped_query still empty after all attempts
        if not wrapped_query:
            return "⚠️ Query regeneration completed, but nothing was returned or executed. Please rephrase."


    # Instead of asking for confirmation via input(), return a prompt to frontend
        query_cache["pending"] = wrapped_query  # 🧠 Save for the next call

        print("✅ Auto-running regenerated query for testing...")
        try:
            result = execute_mongo_query(json.dumps(wrapped_query))
            insert_log(user_query, "EXECUTE", wrapped_query, success=True, matched=len(result))
            return format_mongo_results(result)
        except Exception as e:
            return f"❌ Failed to execute regenerated query: {e}"


    try:

        try:
            # if cleaned_query.strip().startswith("db.") or cleaned_query.strip().startswith("show "):
            #     try:
            #         if "list_collection_names" in cleaned_query:
            #             collections = db.list_collection_names()
            #             return "\n".join([f"📘 {c}" for c in collections])
            #         elif "find_one().keys()" in cleaned_query:
            #             match = re.search(r"db\.(\w+)\.find_one", cleaned_query)
            #             if match:
            #                 coll = match.group(1)
            #                 sample = db[coll].find_one()
            #                 if sample:
            #                     return f"🧾 Fields in `{coll}`:\n" + ", ".join(sample.keys())
            #                 else:
            #                     return f"⚠️ No sample found in `{coll}`"
            #         else:
            #             return f"⚠️ Unrecognized client command: `{cleaned_query}`"
            #     except Exception as e:
            #         return f"❌ Failed to run client command: {e}"
                
            # If it's still not a JSON object, assume it's a client command (e.g., db.collection.find())
            if not cleaned_query.strip().startswith("{") or '"collection"' not in cleaned_query:
                print("⚠️ Treating as client command.")
                try:
                    if "list_collection_names" in cleaned_query:
                        collections = db.list_collection_names()
                        return "\n".join([f"📘 {c}" for c in collections])
                    elif cleaned_query.startswith("show collections"):
                        collections = db.list_collection_names()
                        return "\n\n".join([f"📘 {c}" for c in collections])
                    elif "find_one().keys()" in cleaned_query:
                        coll_name = re.findall(r"db\.(\w+)\.find_one", cleaned_query)
                        if coll_name:
                            sample = db[coll_name[0]].find_one()
                            if sample:
                                return f"🧾 Fields in `{coll_name[0]}`:\n" + ", ".join(sample.keys())
                            else:
                                return f"⚠️ No sample found in `{coll_name[0]}`"
                    return f"⚠️ Unrecognized client command: {cleaned_query}"
                except Exception as e:
                    return f"❌ Failed to run client command: {e}"

            raw_query_dict = json.loads(cleaned_query)
        except json.JSONDecodeError as e:
            print("❌ Could not parse LLM output as valid JSON.")
            print("🧠 LLM returned:\n", cleaned_query)
            insert_log(user_query, "FAIL", cleaned_query, success=False)
            return f"❌ LLM output was not valid JSON: {e}"

        if "ingredient_name" in raw_query_dict:
            wrapped_query = {
                "collection": "ingredient_nutrition",
                "query": raw_query_dict
            }
        elif "commodity" in raw_query_dict:
            wrapped_query = {
                "collection": "food_prices",
                "query": raw_query_dict
            }
        elif "name" in raw_query_dict:
            wrapped_query = {
                "collection": "recipes",
                "query": raw_query_dict
            }
        else:
            wrapped_query = raw_query_dict

        query_dict = wrapped_query.get("query", {})
        if isinstance(wrapped_query.get("query"), dict):
            # Only filter out fields if the original query had keys
            if wrapped_query["query"]:
                query_dict = {
                    k: v for k, v in wrapped_query["query"].items()
                    if v not in [None, "", {}]
                }
                wrapped_query["query"] = query_dict

        # CLEAN QUERY BEFORE EXECUTION
        if isinstance(wrapped_query, dict) and "collection" in wrapped_query and "query" in wrapped_query:
            collection = wrapped_query["collection"]
            valid_fields = get_valid_fields(collection)

            def is_valid_field(key):
                return key in valid_fields or any(key.startswith(f"{v}.") for v in valid_fields)

            removed = [k for k in wrapped_query["query"] if not is_valid_field(k)]
            if removed:
                print(f"⚠️ Removing invalid fields: {removed}")

            filtered_query = {
                k: v for k, v in wrapped_query["query"].items()
                if is_valid_field(k)
            }

            # ⚠️ If empty, regenerate using second LLM
            if not filtered_query:
                if wrapped_query["query"] == {}:
                    # If it's an empty but valid query, don't regenerate
                    print("⚠️ Query is empty but valid ({{}}), skipping regeneration.")
                    results = execute_mongo_query(json.dumps(wrapped_query))
                    print("🔍 Executed query, results:")
                    print(results)
                    insert_log(user_query, "QUERY", wrapped_query, success=bool(results))
                    return format_mongo_results(results)

                # If it's empty and invalid, proceed with LLM regeneration
                print("⚠️ Query is empty after filtering. Attempting regeneration via second LLM...")

                clarification_prompt = f"""
                    The original query became empty after removing invalid or non-existent fields.

                    The schema is:
                    {schema}

                    Original user question:
                    {user_query}

                    The previous query was:
                    {wrapped_query}

                    ---

                    If the original query was empty ({{}}), you may simply return:
                    db.recipes.find({{}}).limit(1)

                    Otherwise, Please regenerate a valid MongoDB query wrapped in:
                    {{
                    "collection": "<collection_name>",
                    "query": {{ ... }},
                    "limit": 1
                    }}
                    
                    Return only one valid query (no explanation), and match the schema exactly.
                    Use only valid fields from the schema.
                    """

                regenerated_query = SYNTAX_LLM.ask_ai(clarification_prompt)

                # Parse JSON from LLM response
                matches = re.findall(r'{[\s\S]+}', regenerated_query)
                if matches:
                    try:
                        new_query = json.loads(matches[0])
                        print("🔁 Recovered query after regeneration:")
                        print(json.dumps(new_query, indent=2))
                        wrapped_query = new_query
                    except Exception as e:
                        return f"<b>Failed to parse regenerated query: {e}</b>"
                else:
                    return "<b>Query could not be regenerated. Try rephrasing.</b>"
                return "⚠️ Query regeneration completed but no output was returned. Please rephrase your question."

            else:
                wrapped_query["query"] = filtered_query


        results = execute_mongo_query(json.dumps(wrapped_query))

        # Debug: Show raw results
        print("✅ Query executed successfully. Raw result preview:")
        print(results)

        # Handle case: No results returned
        if not results:
            print("!! Query was valid but found no matching documents.")
            insert_log(user_query, "QUERY", wrapped_query, success=False)
            return "⚠️ Query was valid but returned no results."

        # Format results safely
        response_text = format_mongo_results(results)

        # Handle case: Formatter returned empty
        if not response_text:
            print("⚠️ format_mongo_results returned empty output.")
            return "⚠️ Query ran successfully but no output was generated."

        # Log and return
        insert_log(user_query, "QUERY", wrapped_query, success=True, matched=len(results))
        print("✅ Formatted response:")
        print(response_text)
        return response_text

        
    
    except Exception as e:
        return f"❌ Mongo query error: {e}"
    

if __name__ == "__main__":
    print("🧠 Welcome to your LLM-powered Recipe Database Assistant.")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            user_input = input("🧑‍🍳 Ask your database a question: ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break
            response = process_query(user_input)
            print("\n📋 Response:\n", response)
            print("\n" + "=" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting via keyboard interrupt.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
