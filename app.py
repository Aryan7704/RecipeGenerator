from flask import Flask, render_template, request
from gemini_recipe_generator import GeminiRecipeGenerator

app = Flask(__name__)
generator = GeminiRecipeGenerator()  # You can pass API key if not hardcoded

@app.route("/", methods=["GET", "POST"])
def index():
    recipe = None
    if request.method == "POST":
        ingredients = request.form.get("ingredients", "").split(",")
        preferences = request.form.get("preferences", "")
        cuisine = request.form.get("cuisine", "")
        meal_type = request.form.get("meal_type", "")
        difficulty = request.form.get("difficulty", "")

        # Clean inputs
        ingredients = [i.strip() for i in ingredients if i.strip()]
        preferences = [p.strip() for p in preferences.split(",") if p.strip()] if preferences else None
        cuisine = cuisine.strip() or None
        meal_type = meal_type.strip() or None
        difficulty = difficulty.strip() or None

        # Generate recipe
        recipe = generator.generate_recipe(
            ingredients,
            preferences=preferences,
            cuisine=cuisine,
            meal_type=meal_type,
            difficulty=difficulty
        )

    return render_template("index.html", recipe=recipe)

if __name__ == "__main__":
    app.run(debug=True)

