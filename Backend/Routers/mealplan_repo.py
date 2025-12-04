from Backend.database import get_db_connection, get_db_cursor
import json
from typing import Optional, List
from datetime import datetime

class MealPlanRepository:
    
    @staticmethod
    def save_meal_plan(user_id: int, meal_plan: str, ingredients_used: Optional[List[str]] = None) -> dict:
        """Save a generated meal plan to history"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            sql = """
                INSERT INTO MealPlanHistory (User_id, Generated_meals, Ingredients_used, 
                                            User_feedback, Energy_levels, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_id,
                json.dumps({"meal_plan": meal_plan}),
                json.dumps(ingredients_used) if ingredients_used else None,
                None,  # user_feedback
                None,  # energy_levels
                datetime.now()
            ))
            
            meal_plan_id = cursor.lastrowid
            
            return {"meal_plan_id": meal_plan_id, "status": "success"}
    
    @staticmethod
    def get_meal_plan_history(user_id: int, limit: int = 10) -> List[dict]:
        """Get meal plan history for a user"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            sql = """
                SELECT * FROM MealPlanHistory 
                WHERE User_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(sql, (user_id, limit))
            results = cursor.fetchall()
            
            # Parse JSON fields
            for result in results:
                if result['Generated_meals']:
                    result['Generated_meals'] = json.loads(result['Generated_meals']) if isinstance(result['Generated_meals'], str) else result['Generated_meals']
                if result['Ingredients_used']:
                    result['Ingredients_used'] = json.loads(result['Ingredients_used']) if isinstance(result['Ingredients_used'], str) else result['Ingredients_used']
                if result['User_feedback']:
                    result['User_feedback'] = json.loads(result['User_feedback']) if isinstance(result['User_feedback'], str) else result['User_feedback']
            
            return results
    
    @staticmethod
    def update_feedback(meal_plan_id: int, feedback: dict, energy_levels: Optional[str] = None) -> dict:
        """Update user feedback for a meal plan"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            sql = """
                UPDATE MealPlanHistory 
                SET User_feedback = %s, Energy_levels = %s
                WHERE id = %s
            """
            cursor.execute(sql, (
                json.dumps(feedback),
                energy_levels,
                meal_plan_id
            ))
            
            return {"status": "success", "updated_rows": cursor.rowcount}
