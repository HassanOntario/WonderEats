from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    name: str
    age: int
    height_cm: float
    weight_kg: float
    goals: str  # e.g., "lose_fat", "gain_muscle", "maintain"
    budget_per_week: Optional[float]

class UserNutritionProfile(BaseModel):
    bmr: float
    tdee: float # Total Daily Energy Expenditure
    maintenance_calories: float
    allergies: List[str]

class UserPreferences(BaseModel):
    favorite_cuisines: Optional[List[str]]
    disliked_ingredients: Optional[List[str]]
    meal_frequency: int  # meals per day
    snack_preference: Optional[bool]

class UserInsights(BaseModel):
    cultural_context: Optional[str]
    lifestyle_habits: Optional[str]
    health_conditions: Optional[List[str]]
    energy_levels: Optional[str]