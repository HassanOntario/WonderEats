# agents/meal_agent.py
import google.generativeai as genai
from Backend.Models.user_models import UserFullProfile
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_mealplan(data: UserFullProfile):
    # Create the model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Create the prompt
    system_instruction = (
        "You are a personalized meal plan generator.\n"
        "Use the provided user profile JSON as the single source of truth.\n"
        "Generate a meal plan aligned with goals, nutrition needs,\n"
        "preferences, lifestyle insights, and allergies."
    )
    
    user_data = json.dumps(data.model_dump(), indent=2)
    prompt = f"{system_instruction}\n\nUser Profile:\n{user_data}"
    
    # Generate content
    response = await model.generate_content_async(prompt)
    
    return response.text
