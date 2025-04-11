import requests
import json
import os
import random
from datetime import datetime

class GeminiRecipeGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or 'AIzaSyAagh9NiZlZNEg-so--9ZbvYSe60TN63Og'
        if not self.api_key:
            print("Warning: No API key provided. ")
        
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
        
        self.cuisine_styles = ["Italian", "Mexican", "Asian", "Mediterranean", "American", "Indian", "French", "Middle Eastern"]
        self.meal_types = ["breakfast", "lunch", "dinner", "appetizer", "dessert", "snack"]
        
        self.ingredient_categories = {
            "proteins": ["chicken", "beef", "pork", "tofu", "tempeh", "beans", "lentils", "chickpeas", "eggs", "fish", "shrimp"],
            "vegetables": ["onion", "garlic", "carrot", "bell pepper", "tomato", "spinach", "broccoli", "cucumber", "zucchini", "potato"],
            "grains": ["rice", "pasta", "quinoa", "couscous", "bread", "tortilla", "oats", "barley"],
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "sour cream"],
            "fruits": ["apple", "banana", "orange", "berries", "lemon", "lime", "avocado"],
            "herbs_spices": ["basil", "cilantro", "parsley", "rosemary", "thyme", "oregano", "cumin", "paprika", "cinnamon", "nutmeg"],
            "condiments": ["olive oil", "soy sauce", "vinegar", "mustard", "honey", "maple syrup", "ketchup", "mayonnaise"]
        }
        
        self.dietary_preferences = ["vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb", "keto", "paleo"]

    def categorize_ingredients(self, ingredients):
        categorized = {}
        for category in self.ingredient_categories:
            categorized[category] = []

        uncategorized = []

        for ingredient in ingredients:
            ingredient = ingredient.lower().strip()
            found = False
            for category, items in self.ingredient_categories.items():
                for item in items:
                    if item in ingredient:
                        categorized[category].append(ingredient)
                        found = True
                        break
                if found:
                    break
            if not found:
                uncategorized.append(ingredient)

        return categorized, uncategorized

    def analyze_ingredients(self, ingredients):
        categorized, uncategorized = self.categorize_ingredients(ingredients)
        suggested_cuisines = []

        for i in ingredients:
            if "rice" in i and "soy" in i:
                suggested_cuisines.append("Asian")
                break
        for i in ingredients:
            if "pasta" in i and "tomato" in i:
                suggested_cuisines.append("Italian")
                break
        for i in ingredients:
            if "tortilla" in i and ("cilantro" in i or "lime" in i):
                suggested_cuisines.append("Mexican")
                break
        for i in ingredients:
            if "chickpea" in i and "lemon" in i:
                suggested_cuisines.append("Mediterranean")
                break
        for i in ingredients:
            if "curry" in i or "garam masala" in i:
                suggested_cuisines.append("Indian")
                break

        if not suggested_cuisines:
            joined_proteins = " ".join(categorized["proteins"])
            joined_spices = " ".join(categorized["herbs_spices"])
            if "tofu" in joined_proteins:
                suggested_cuisines.append("Asian")
            elif "beans" in joined_proteins:
                suggested_cuisines.append("Mexican")
            if "basil" in joined_spices:
                suggested_cuisines.append("Italian")
            elif "cilantro" in joined_spices:
                suggested_cuisines.append("Mexican")
            elif "rosemary" in joined_spices:
                suggested_cuisines.append("Mediterranean")

        if not suggested_cuisines:
            count = min(2, len(self.cuisine_styles))
            for i in range(count):
                suggested_cuisines.append(self.cuisine_styles[i])

        suggested_meal_types = []
        for i in ingredients:
            if "egg" in i and not ("pasta" in i or "rice" in i):
                suggested_meal_types.append("breakfast")
                break
        for i in ingredients:
            if "flour" in i and ("sugar" in i or "chocolate" in i):
                suggested_meal_types.append("dessert")
                break
        for i in ingredients:
            if "bread" in i and len(ingredients) < 6:
                suggested_meal_types.append("sandwich")
                suggested_meal_types.append("lunch")
                break

        if not suggested_meal_types:
            current_hour = datetime.now().hour
            if 5 <= current_hour < 10:
                suggested_meal_types.append("breakfast")
            elif 10 <= current_hour < 14:
                suggested_meal_types.append("lunch")
            elif 17 <= current_hour < 21:
                suggested_meal_types.append("dinner")
            else:
                suggested_meal_types.append(random.choice(["dinner", "snack"]))

        return {
            "categorized_ingredients": categorized,
            "uncategorized_ingredients": uncategorized,
            "suggested_cuisines": suggested_cuisines,
            "suggested_meal_types": suggested_meal_types
        }

    def identify_dietary_preferences(self, ingredients):
        preferences = []
        combined_ingredients = " ".join(ingredients).lower()
        meat_products = ["chicken", "beef", "pork", "fish", "shrimp", "lamb", "turkey"]
        dairy_products = ["milk", "cheese", "yogurt", "butter", "cream"]
        gluten_products = ["wheat", "flour", "pasta", "bread", "couscous", "barley"]

        is_vegetarian = True
        for meat in meat_products:
            if meat in combined_ingredients:
                is_vegetarian = False
                break

        if is_vegetarian:
            preferences.append("vegetarian")
            is_vegan = True
            for dairy in dairy_products:
                if dairy in combined_ingredients:
                    is_vegan = False
                    break
            if is_vegan:
                preferences.append("vegan")

        is_gluten_free = True
        for gluten in gluten_products:
            if gluten in combined_ingredients:
                is_gluten_free = False
                break
        if is_gluten_free:
            preferences.append("gluten-free")

        is_dairy_free = True
        for dairy in dairy_products:
            if dairy in combined_ingredients:
                is_dairy_free = False
                break
        if is_dairy_free:
            preferences.append("dairy-free")

        return preferences

    def generate_recipe_prompt(self, ingredients, preferences=None, cuisine=None, meal_type=None, difficulty=None):
        if not cuisine or not meal_type:
            analysis = self.analyze_ingredients(ingredients)
            if not cuisine and analysis["suggested_cuisines"]:
                cuisine = random.choice(analysis["suggested_cuisines"])
            if not meal_type and analysis["suggested_meal_types"]:
                meal_type = random.choice(analysis["suggested_meal_types"])

        if not cuisine:
            cuisine = random.choice(self.cuisine_styles)
        if not meal_type:
            meal_type = random.choice(self.meal_types)
        if not difficulty:
            difficulty = random.choice(["easy", "intermediate", "advanced"])

        if not preferences:
            preferences = self.identify_dietary_preferences(ingredients)

        ingredients_str = ""
        for item in ingredients:
            ingredients_str += item + ", "
        ingredients_str = ingredients_str.rstrip(", ")

        if preferences:
            preferences_str = ", ".join(preferences)
        else:
            preferences_str = "any diet"

        prompt = f"""Create a unique {cuisine} {meal_type} recipe using these ingredients: {ingredients_str}.

The recipe should be:
- {difficulty.title()} difficulty level
- Creative but practical
- Include all or most of the listed ingredients
- Suitable for {preferences_str}

Please format the recipe with:
1. A catchy, creative name
2. Brief description and cultural background
3. Prep time and cooking time
4. Complete ingredients list with measurements
5. Clear step-by-step instructions
6. Serving suggestion with plating tips
7. One cooking tip or secret technique
8. Nutritional benefits of key ingredients

Be creative but ensure the recipe is practical and delicious!
"""
        return prompt

    def call_gemini_api(self, prompt):
        if not self.api_key:
            return {"error": "No API key available. Set GEMINI_API_KEY environment variable or provide it directly."}

        params = {
            "key": self.api_key
        }

        data = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7,"maxOutputTokens": 1500}
        }

        try:
            response = requests.post(self.api_url, params=params, json=data)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Response parsing error: {str(e)}"

    def generate_recipe(self, ingredients, preferences=None, cuisine=None, meal_type=None, difficulty=None):
        prompt = self.generate_recipe_prompt(
            ingredients,
            preferences=preferences,
            cuisine=cuisine,
            meal_type=meal_type,
            difficulty=difficulty
        )
        recipe = self.call_gemini_api(prompt)
        return recipe



def get_recipe_from_terminal():
    generator = GeminiRecipeGenerator()

    if not generator.api_key:
        api_key = 'AIzaSyAagh9NiZlZNEg-so--9ZbvYSe60TN63Og'
        if api_key.strip():
            generator.api_key = api_key
        else:
            print("No API key provided. Running in demo mode (no API calls).")

    print("\nWelcome to the Gemini Recipe Generator!")

    print("\nEnter the ingredients you have (comma separated):")
    user_input = input("> ")
    ingredients = []
    for i in user_input.split(","):
        ingredients.append(i.strip())

    print("\nAny dietary preferences? (vegetarian, vegan, gluten-free, etc.)")
    print("Press Enter to skip")
    preferences_input = input("> ")
    preferences = None
    if preferences_input:
        preferences = []
        for p in preferences_input.split(","):
            preferences.append(p.strip())

    print("\nPreferred cuisine? (Italian, Mexican, Asian, etc.)")
    print("Press Enter for suggestions")
    cuisine = input("> ").strip() or None

    print("\nWhat meal are you preparing? (breakfast, lunch, dinner, dessert)")
    print("Press Enter for suggestions")
    meal_type = input("> ").strip() or None

    print("\nDifficulty level? (easy, intermediate, advanced)")
    print("Press Enter for any difficulty")
    difficulty = input("> ").strip() or None

# # printing all the inputs
#     print("Ingredients:", ingredients)
#     print("Preferences:", preferences)
#     print("Cuisine:", cuisine)
#     print("Meal type:", meal_type)
#     print("Difficulty:", difficulty)
#     print(generator.generate_recipe_prompt(ingredients, preferences, cuisine, meal_type, difficulty))


# final Output (response from the gemini)
    print("\nGenerating your personalized recipe with Gemini AI... 🧠👨‍🍳")

    recipe = generator.generate_recipe(ingredients, preferences=preferences, cuisine=cuisine, meal_type=meal_type, difficulty=difficulty)
    print("\n" + "="*80 + "\n")
    print(recipe)
    print("\n" + "="*80)



if __name__ == "__main__":
    get_recipe_from_terminal()