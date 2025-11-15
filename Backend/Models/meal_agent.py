# agents/meal_agent.py
from openai import AsyncOpenAI
from user_models import user, UserNutritionProfile, UserPreferences, UserInsights

client = AsyncOpenAI()

async def generate_mealplan(data: MealPlanInput):
    prompt = f"""
    Create a {data.goals} meal plan for someone with:
    - restrictions: {data.dietary_restrictions}
    - ingredients available: {data.ingredients_on_hand}
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content