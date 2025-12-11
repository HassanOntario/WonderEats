from fastapi import APIRouter, HTTPException
from typing import Optional, List
from Backend.Models.user_models import UserFullProfile
from Backend.Agents.meal_agent import generate_mealplan
from Backend.Routers.users_repo import UsersRepository
from Backend.Routers.mealplan_repo import MealPlanRepository
from Backend.Routers.recipe_repo import RecipeRepository

router = APIRouter()
recipe_repo = RecipeRepository()

# ==================== USER ENDPOINTS ====================

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

# ==================== MEAL PLAN ENDPOINTS ====================

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

# ==================== RECIPE ENDPOINTS ====================

@router.post("/recipes/import")
async def import_recipes(goal: str, cuisine: Optional[str] = None, limit: int = 50):
    """
    Import recipes from external APIs into BOTH MySQL and ChromaDB
    
    Args:
        goal: 'lose_fat', 'gain_muscle', or 'maintain'
        cuisine: Optional cuisine filter (e.g., 'Mediterranean', 'Asian')
        limit: Maximum number of recipes to import
    """
    try:
        result = await recipe_repo.seed_from_apis(goal, cuisine, limit)
        return {
            "status": "success",
            "message": f"Imported {result['imported']} recipes",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipes/search")
async def search_recipes(
    goal: str,
    cuisines: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    limit: int = 10
):
    """
    Search recipes using vector similarity (ChromaDB) and fetch from MySQL
    
    Args:
        goal: 'lose_fat', 'gain_muscle', or 'maintain'
        cuisines: List of preferred cuisines
        allergies: List of allergens to avoid
        limit: Maximum number of results
    """
    try:
        results = recipe_repo.search_recipes(
            goal=goal,
            preferences=cuisines,
            allergies=allergies,
            n_results=limit
        )
        return {
            "status": "success",
            "count": len(results),
            "recipes": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID from MySQL"""
    try:
        recipe = recipe_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return {
            "status": "success",
            "recipe": recipe
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipes/stats/database")
async def get_database_stats():
    """Get statistics about MySQL and ChromaDB sync status"""
    try:
        stats = recipe_repo.get_database_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
