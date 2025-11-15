# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional
#
# app = FastAPI()
#
# class UserNutritionProfile(BaseModel):
#     name: str
#     age: int
#     sex: str
#     height_cm: float
#     weight_kg: float
#     activity_level: str  # sedentary, moderate, active
#     goal: str  # lose_fat, gain_muscle, maintain
#     dietary_preferences: List[str]
#     allergies: List[str]
#     budget_per_week: Optional[float]
#     cooking_time_limit: int  # minutes
#     cultural_context: Optional[str]
#
# class UserPreferences(BaseModel):
#     favorite_cuisines: List[str]
#     disliked_ingredients: List[str]
#     meal_frequency: int  # meals per day
#     snack_preference: bool
#
# class UserInsights(BaseModel):
#     cultural_context: Optional[str]
#     lifestyle_habits: Optional[str]
#     health_conditions: Optional[List[str]]
#     energy_levels: Optional[str]
#
# class MealPlanInput(BaseModel):
#     goals: str
#     dietary_restrictions: list[str]
#     ingredients_on_hand: list[str]