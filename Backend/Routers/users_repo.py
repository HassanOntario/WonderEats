from Backend.database import get_db_connection, get_db_cursor
from Backend.Models.user_models import UserFullProfile, User, UserNutritionProfile, UserPreferences, UserInsights
import json
from typing import Optional

class UsersRepository:
    
    @staticmethod
    def create_user(user_data: UserFullProfile) -> dict:
        """Create a new user with all related profiles"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            # Insert User
            user_sql = """
                INSERT INTO User (Name, Age, Height_cm, Weight_kg, Goals, Budget_weekly, 
                                 Scheduling_constraints, Equipment_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(user_sql, (
                user_data.user.name,
                user_data.user.age,
                user_data.user.height_cm,
                user_data.user.weight_kg,
                json.dumps(user_data.user.goals),
                user_data.user.budget_per_week,
                None,  # scheduling_constraints
                None   # equipment_available
            ))
            user_id = cursor.lastrowid
            
            # Insert UserNutritionProfile
            nutrition_sql = """
                INSERT INTO UserNutritionProfile (BMR, TDEE, Maintenance_cals, Allergies, 
                                                  Dietary_identities, User_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(nutrition_sql, (
                user_data.nutrition.bmr,
                user_data.nutrition.tdee,
                user_data.nutrition.maintenance_calories,
                json.dumps(user_data.nutrition.allergies),
                None,  # dietary_identities
                user_id
            ))
            
            # Insert UserPreferences
            preferences_sql = """
                INSERT INTO UserPreferences (Favorite_cuisines, Disliked_ingredients, 
                                            Meal_frequency, Snack_preference, User_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(preferences_sql, (
                json.dumps(user_data.preferences.favorite_cuisines),
                json.dumps(user_data.preferences.disliked_ingredients),
                user_data.preferences.meal_frequency,
                user_data.preferences.snack_preference,
                user_id
            ))
            
            # Insert UserInsights
            insights_sql = """
                INSERT INTO UserInsights (Cultural_context, Lifestyle_habits, 
                                         Health_conditions, Energy_levels, User_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insights_sql, (
                json.dumps(user_data.insights.cultural_context),
                json.dumps(user_data.insights.lifestyle_habits),
                json.dumps(user_data.insights.health_conditions),
                user_data.insights.energy_levels,
                user_id
            ))
            
            return {"user_id": user_id, "status": "success"}
    
    @staticmethod
    def get_user(user_id: int) -> Optional[UserFullProfile]:
        """Retrieve a user with all related profiles"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            # Get User
            cursor.execute("SELECT * FROM User WHERE id = %s", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            # Get UserNutritionProfile
            cursor.execute("SELECT * FROM UserNutritionProfile WHERE User_id = %s", (user_id,))
            nutrition_row = cursor.fetchone()
            
            # Get UserPreferences
            cursor.execute("SELECT * FROM UserPreferences WHERE User_id = %s", (user_id,))
            preferences_row = cursor.fetchone()
            
            # Get UserInsights
            cursor.execute("SELECT * FROM UserInsights WHERE User_id = %s", (user_id,))
            insights_row = cursor.fetchone()
            
            # Build UserFullProfile
            user = User(
                user_id=str(user_row['id']),
                name=user_row['Name'],
                age=user_row['Age'],
                height_cm=user_row['Height_cm'],
                weight_kg=user_row['Weight_kg'],
                goals=json.loads(user_row['Goals']) if isinstance(user_row['Goals'], str) else user_row['Goals'],
                budget_per_week=user_row['Budget_weekly']
            )
            
            nutrition = UserNutritionProfile(
                bmr=nutrition_row['BMR'],
                tdee=nutrition_row['TDEE'],
                maintenance_calories=nutrition_row['Maintenance_cals'],
                allergies=json.loads(nutrition_row['Allergies']) if nutrition_row['Allergies'] else []
            )
            
            preferences = UserPreferences(
                favorite_cuisines=json.loads(preferences_row['Favorite_cuisines']) if preferences_row['Favorite_cuisines'] else None,
                disliked_ingredients=json.loads(preferences_row['Disliked_ingredients']) if preferences_row['Disliked_ingredients'] else None,
                meal_frequency=preferences_row['Meal_frequency'],
                snack_preference=preferences_row['Snack_preference']
            )
            
            insights = UserInsights(
                cultural_context=json.loads(insights_row['Cultural_context']) if insights_row['Cultural_context'] else None,
                lifestyle_habits=json.loads(insights_row['Lifestyle_habits']) if insights_row['Lifestyle_habits'] else None,
                health_conditions=json.loads(insights_row['Health_conditions']) if insights_row['Health_conditions'] else None,
                energy_levels=insights_row['Energy_levels']
            )
            
            return UserFullProfile(
                user=user,
                nutrition=nutrition,
                preferences=preferences,
                insights=insights
            )
    
    @staticmethod
    def user_exists(user_id: int) -> bool:
        """Check if a user exists"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT COUNT(*) as count FROM User WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result['count'] > 0
