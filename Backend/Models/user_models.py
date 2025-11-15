from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    user_id: str
    name: str
    age: int
    height_cm: float
    weight_kg: float
    goals: str  # e.g., "lose_fat", "gain_muscle", "maintain"
    budget_per_week: Optional[float] = None

class UserNutritionProfile(BaseModel):
    bmr: float
    tdee: float # Total Daily Energy Expenditure
    maintenance_calories: float
    allergies: List[str] = []

class UserPreferences(BaseModel):
    favorite_cuisines: Optional[List[str]] = None
    disliked_ingredients: Optional[List[str]] = None
    meal_frequency: int  # meals per day
    snack_preference: Optional[bool] = None

class UserInsights(BaseModel):
    cultural_context: Optional[str] = None
    lifestyle_habits: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    energy_levels: Optional[str] = None

class UserFullProfile(BaseModel):
    user: User
    nutrition: UserNutritionProfile
    preferences: UserPreferences
    insights: UserInsights