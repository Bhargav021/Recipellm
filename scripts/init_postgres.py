import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def get_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value if value is not None else default


def ensure_database_exists(db_name: str, user: str, password: str, host: str, port: str) -> None:
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host=host,
        port=port,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone() is not None
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(db_name)))
        print(f"Created database '{db_name}'.")
    else:
        print(f"Database '{db_name}' already exists.")
    cur.close()
    conn.close()


def run_schema(db_name: str, user: str, password: str, host: str, port: str) -> None:
    conn = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port,
    )
    conn.autocommit = True
    cur = conn.cursor()

    statements = [
        """
        CREATE TABLE IF NOT EXISTS recipes (
            recipeid INT PRIMARY KEY,
            name TEXT,
            recipeingredientparts TEXT[],
            recipecategory TEXT,
            calories NUMERIC,
            fatcontent NUMERIC,
            carbohydratecontent NUMERIC,
            proteincontent NUMERIC,
            recipeinstructions TEXT[],
            aggregatedrating NUMERIC,
            reviewcount NUMERIC
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS ingredient_nutrition (
            id SERIAL PRIMARY KEY,
            fdc_id BIGINT,
            ingredient_name TEXT,
            food_category_id BIGINT,
            category_name TEXT,
            portion_description TEXT,
            gram_weight NUMERIC,
            calcium_mg NUMERIC,
            carbohydrate_g NUMERIC,
            energy_kcal NUMERIC,
            energy_kj NUMERIC,
            fiber_g NUMERIC,
            folate_ug NUMERIC,
            iron_mg NUMERIC,
            magnesium_mg NUMERIC,
            potassium_mg NUMERIC,
            protein_g NUMERIC,
            sodium_mg NUMERIC,
            fat_g NUMERIC,
            vitamin_a_rae_ug NUMERIC,
            vitamin_b12_ug NUMERIC,
            vitamin_c_ascorbic_ug NUMERIC,
            vitamin_d_ug NUMERIC,
            zinc_mg NUMERIC
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS food_prices (
            id SERIAL PRIMARY KEY,
            countryiso3 TEXT,
            date DATE,
            market TEXT,
            category TEXT,
            commodity TEXT,
            unit TEXT,
            price NUMERIC,
            usdprice NUMERIC
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id SERIAL PRIMARY KEY,
            recipe_id INT,
            ingredient_id INT,
            ingredient_name TEXT,
            fdc_id BIGINT,
            CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES recipes(recipeid) ON DELETE CASCADE,
            CONSTRAINT fk_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient_nutrition(id) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            user_query TEXT,
            action_type TEXT,
            executed_sql TEXT,
            related_table TEXT,
            ingredient_id INT,
            recipe_id INT,
            price_id INT
        );
        """,
    ]

    for stmt in statements:
        cur.execute(stmt)

    print("Schema initialization completed.")
    cur.close()
    conn.close()


def main() -> None:
    load_dotenv()
    db_name = get_env("DB_NAME", "recipe_chatbot")
    db_user = get_env("DB_USER", "postgres")
    db_password = get_env("DB_PASSWORD", "")
    db_host = get_env("DB_HOST", "localhost")
    db_port = get_env("DB_PORT", "5432")

    ensure_database_exists(db_name, db_user, db_password, db_host, db_port)
    run_schema(db_name, db_user, db_password, db_host, db_port)


if __name__ == "__main__":
    main()
