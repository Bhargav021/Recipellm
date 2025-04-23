TABLE: recipes
- RecipeId INT PRIMARY KEY
- Name TEXT
- RecipeIngredientParts TEXT[]
- RecipeCategory TEXT
- Calories NUMERIC
- FatContent NUMERIC
- CarbohydrateContent NUMERIC
- ProteinContent NUMERIC
- RecipeInstructions TEXT
- AggregatedRating NUMERIC
- ReviewCount NUMERIC

TABLE: ingredient_nutrition
- id SERIAL PRIMARY KEY
- fdc_id BIGINT NOT NULL
- ingredient_name TEXT
- [various nutrient columns such as protein_g, fat_g, etc.]

TABLE: food_prices
- id SERIAL PRIMARY KEY
- commodity TEXT
- countryiso3 TEXT
- market TEXT
- date DATE
- price NUMERIC
- usdprice NUMERIC

TABLE: recipe_ingredients
- id SERIAL PRIMARY KEY
- recipe_id → recipes(RecipeId)
- ingredient_id → ingredient_nutrition(id)
- ingredient_name (TEXT)
- fdc_id (BIGINT)
