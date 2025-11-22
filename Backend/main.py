from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from Backend.Models.user_models import UserFullProfile
from Backend.Agents.meal_agent import generate_mealplan
import asyncio

app = FastAPI()

# In-memory storage (replace with database later)
users_db = {}

@app.post("/users/create")
async def create_user(user_data: UserFullProfile):
    """Create or update a user profile"""
    user_id = user_data.user.user_id
    users_db[user_id] = user_data
    return {"status": "success", "user_id": user_id, "message": "User profile created"}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Retrieve a user profile"""
    if user_id not in users_db:
        return {"status": "error", "message": "User not found"}
    return users_db[user_id]

@app.post("/mealplan/generate/{user_id}")
async def generate_meal_plan(user_id: str):
    """Generate a meal plan for a user"""
    if user_id not in users_db:
        return {"status": "error", "message": "User not found"}
    
    user_data = users_db[user_id]
    meal_plan = await generate_mealplan(user_data)
    
    return {
        "status": "success",
        "user_id": user_id,
        "meal_plan": meal_plan
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)