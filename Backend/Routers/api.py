from fastapi import APIRouter, HTTPException
from typing import Optional
from Backend.Models.user_models import UserFullProfile
from Backend.Agents.meal_agent import generate_mealplan
from Backend.Routers.users_repo import UsersRepository
from Backend.Routers.mealplan_repo import MealPlanRepository

router = APIRouter()

@router.post("/users")
async def create_user(user_data: UserFullProfile):
    """Create or update a user profile"""
    try:
        result = UsersRepository.create_user(user_data)
        return {"status": "success", "user_id": result["user_id"], "message": "User profile created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Retrieve a user profile"""
    user_data = UsersRepository.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

@router.post("/users/{user_id}/mealplans")
async def generate_meal_plan(user_id: int):
    """Generate a meal plan for a user"""
    # Check if user exists
    if not UsersRepository.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user data
    user_data = UsersRepository.get_user(user_id)
    
    # Generate meal plan
    meal_plan = await generate_mealplan(user_data)
    
    # Save to history
    save_result = MealPlanRepository.save_meal_plan(user_id, meal_plan)
    
    return {
        "status": "success",
        "user_id": user_id,
        "meal_plan": meal_plan,
        "meal_plan_id": save_result["meal_plan_id"]
    }

@router.get("/users/{user_id}/mealplans")
async def get_meal_plan_history(user_id: int, limit: int = 10):
    """Get meal plan history for a user"""
    if not UsersRepository.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    history = MealPlanRepository.get_meal_plan_history(user_id, limit)
    return {
        "status": "success",
        "user_id": user_id,
        "history": history
    }

@router.post("/mealplans/{meal_plan_id}/feedback")
async def submit_feedback(meal_plan_id: int, feedback: dict, energy_levels: Optional[str] = None):
    """Submit feedback for a meal plan"""
    try:
        result = MealPlanRepository.update_feedback(meal_plan_id, feedback, energy_levels)
        return {"status": "success", "message": "Feedback submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
