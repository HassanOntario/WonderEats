# agents/meal_agent.py
import google.generativeai as genai
from Backend.Models.user_models import UserFullProfile
# ^ 1. load from SQL database, not pydantic model
from Backend.Routers.recipe_repo import RecipeRepository
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_mealplan(data: UserFullProfile):
    # ^1. load from SQL database, not pydantic model
    """
    Generate a personalized meal plan using RAG (Retrieval Augmented Generation).
    
    Flow:
    1. Search vector database for recipes matching user's goals and preferences
    2. Retrieve full recipe data from MySQL
    3. Pass user profile + relevant recipes to Gemini for meal plan generation
    """
    
    # Initialize recipe repository
    repo = RecipeRepository()
    
    # Extract user preferences for recipe search
    user_goal = data.user.goals  # e.g., 'lose_fat', 'gain_muscle', 'maintain'
    cuisine_preferences = data.preferences.favorite_cuisines or []
    allergies = data.nutrition.allergies or []
    
    # Search for relevant recipes (get more than needed for variety)
    num_days = 7  # Generate a week's worth of meals
    meals_per_day = data.preferences.meal_frequency or 3
    total_meals_needed = num_days * meals_per_day
    
    # AGGRESSIVE OPTIMIZATION: Retrieve exactly what's needed (21 recipes for 7 days × 3 meals)
    # This gives Gemini just enough variety without wasting tokens
    #
    # 21 recipes × 50 tokens = ~1,050 tokens (was ~2,480 with 31 recipes)
    # ^2. token optimization needed. send ids instead of full recipes
    relevant_recipes = repo.search_recipes(
        goal=user_goal,
        preferences=cuisine_preferences if cuisine_preferences else None,
        allergies=allergies if allergies else None,
        n_results=total_meals_needed
    )
    
    # Format recipes for the prompt
    recipes_text = _format_recipes_for_prompt(relevant_recipes)
    
    # ULTRA-COMPACT system instruction (50 tokens instead of 500)
    system_instruction = """Create 7-day meal plan. Use ONLY recipes below. Match goal (lose_fat=-500cal, gain_muscle=+300cal, maintain=TDEE). Avoid allergies. Return JSON: {"days":[{"day":1,"meals":[{"type":"breakfast","recipe":"Name","cal":400}]}],"shopping_list":["item"]}"""
    
    # Build the complete prompt
    user_data = json.dumps(data.model_dump(), indent=2)
    
    # MINIMALIST USER PROFILE: Only send essential fields
    # Extract just what Gemini needs - no fluff
    user_summary = {
        "goal": user_goal,
        "tdee": data.nutrition.tdee,
        "allergies": allergies,
        "cuisines": cuisine_preferences,
        "meals_per_day": meals_per_day
    }
    user_data_compact = json.dumps(user_summary)
    
    # ULTRA-COMPACT PROMPT: Removed headers and extra text
    prompt = f"""{system_instruction}

RECIPES:
{recipes_text}

USER: {user_data_compact}"""
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = await model.generate_content_async(prompt)
    
    return response.text


def _format_recipes_for_prompt(recipes: list) -> str:
    #^3. recipe formatting to be revisited
    """Ultra-compact recipe format: ~50 tokens per recipe (was ~175)
    
    Format: #1 RecipeName|Cuisine|Cal:X P:Xg C:Xg F:Xg
    - Removed ingredients (Gemini doesn't need them for meal planning)
    - Removed source, fiber, description
    - Minimal whitespace
    """
    if not recipes:
        return "No recipes."
    
    formatted = []
    for i, recipe in enumerate(recipes, 1):
        nutrition = recipe.get('nutrition', {})
        if isinstance(nutrition, str):
            nutrition = json.loads(nutrition)
        
        # ULTRA-COMPACT: Just name, cuisine, and macros
        recipe_text = (
            f"#{i} {recipe.get('name', 'Unknown')}|{recipe.get('cuisine', 'N/A')}|"
            f"Cal:{nutrition.get('calories', 0)} P:{nutrition.get('protein', 0)}g "
            f"C:{nutrition.get('carbohydrates', 0)}g F:{nutrition.get('fat', 0)}g"
        )
        formatted.append(recipe_text)
    
    return "\n".join(formatted)
