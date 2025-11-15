# agents/meal_agent.py
from openai import AsyncOpenAI
from Backend.Models.user_models import UserFullProfile
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_mealplan(data: UserFullProfile):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a personalized meal plan generator.\n"
                    "Use the provided user profile JSON as the single source of truth.\n"
                    "Generate a meal plan aligned with goals, nutrition needs,\n"
                    "preferences, lifestyle insights, and allergies."
                )
            },
            {
                "role": "user",
                "content": json.dumps(data.model_dump(), indent=2)
            }
        ]
    )
    return response.choices[0].message.content
