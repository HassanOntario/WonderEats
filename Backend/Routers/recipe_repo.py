from Backend.database import get_db_connection, get_db_cursor
from Backend.Services.recipe_importer import RecipeImporter
from Backend.Services.recipe_embedder import RecipeVectorStore
import json
from typing import List, Dict, Optional

class RecipeRepository:
    """Central repository managing recipe data across MySQL and ChromaDB"""
    
    def __init__(self):
        self.importer = RecipeImporter()
        self.vector_store = RecipeVectorStore()
    
    async def seed_from_apis(self, goal: str, cuisine: Optional[str] = None, limit: int = 50) -> Dict:
        """
        Seed database from external APIs → MySQL → ChromaDB
        This writes to BOTH databases
        """
        print(f"Fetching {limit} recipes for goal: {goal}, cuisine: {cuisine or 'all'}")
        
        # 1. Fetch from APIs
        recipes = await self.importer.fetch_recipes_by_goal(goal, cuisine, limit)
        
        if not recipes:
            return {"imported": 0, "saved_mysql": 0, "saved_vector": 0}
        
        # 2. Save to MySQL (source of truth)
        saved_count = 0
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            for recipe in recipes:
                try:
                    cursor.execute("""
                        INSERT INTO Recipes 
                        (id, name, source, cuisine, description, nutrition, ingredients, instructions, tags, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON DUPLICATE KEY UPDATE 
                            last_updated = NOW()
                    """, (
                        recipe['id'],
                        recipe['name'],
                        recipe['source'],
                        recipe['cuisine'],
                        recipe.get('description', ''),
                        json.dumps(recipe['nutrition']),
                        json.dumps(recipe['ingredients']),
                        recipe.get('instructions', ''),
                        json.dumps(recipe.get('tags', []))
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"Error saving recipe {recipe['id']} to MySQL: {e}")
        
        # 3. Sync to ChromaDB
        self.vector_store.add_recipes(recipes)
        
        return {
            "imported": len(recipes), 
            "saved_mysql": saved_count,
            "saved_vector": len(recipes)
        }
    
    def search_recipes(
        self,
        goal: str,
        preferences: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        n_results: int = 15
    ) -> List[Dict]:
        """
        Search workflow: ChromaDB (get IDs) → MySQL (get full data)
        """
        # 1. Semantic search in ChromaDB (FAST)
        vector_results = self.vector_store.search_by_goals_and_taste(
            goal=goal,
            preferences=preferences,
            allergies=allergies,
            n_results=n_results
        )
        
        if not vector_results:
            return []
        
        # 2. Get recipe IDs
        recipe_ids = [r['recipe_id'] for r in vector_results]
        
        # 3. Fetch full data from MySQL
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            placeholders = ','.join(['%s'] * len(recipe_ids))
            cursor.execute(f"""
                SELECT id, name, cuisine, description, nutrition, ingredients, instructions, tags
                FROM Recipes
                WHERE id IN ({placeholders})
            """, recipe_ids)
            
            full_recipes = cursor.fetchall()
        
        # 4. Parse JSON fields
        for recipe in full_recipes:
            recipe['nutrition'] = json.loads(recipe['nutrition']) if isinstance(recipe['nutrition'], str) else recipe['nutrition']
            recipe['ingredients'] = json.loads(recipe['ingredients']) if isinstance(recipe['ingredients'], str) else recipe['ingredients']
            recipe['tags'] = json.loads(recipe.get('tags', '[]')) if isinstance(recipe.get('tags'), str) else recipe.get('tags', [])
        
        return full_recipes
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict]:
        """Get single recipe from MySQL"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("""
                SELECT id, name, cuisine, description, nutrition, ingredients, instructions, tags
                FROM Recipes
                WHERE id = %s
            """, (recipe_id,))
            
            recipe = cursor.fetchone()
            
            if recipe:
                recipe['nutrition'] = json.loads(recipe['nutrition']) if isinstance(recipe['nutrition'], str) else recipe['nutrition']
                recipe['ingredients'] = json.loads(recipe['ingredients']) if isinstance(recipe['ingredients'], str) else recipe['ingredients']
                recipe['tags'] = json.loads(recipe.get('tags', '[]')) if isinstance(recipe.get('tags'), str) else recipe.get('tags', [])
            
            return recipe
    
    def track_recipe_usage(self, user_id: int, meal_plan_id: int, recipe_ids: List[str]):
        """Track which recipes were used in meal plans (MySQL only)"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            for recipe_id in recipe_ids:
                try:
                    cursor.execute("""
                        INSERT INTO RecipeUsage (user_id, meal_plan_id, recipe_id, created_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (user_id, meal_plan_id, recipe_id))
                    
                    # Increment popularity
                    cursor.execute("""
                        UPDATE Recipes
                        SET popularity_score = popularity_score + 1
                        WHERE id = %s
                    """, (recipe_id,))
                except Exception as e:
                    print(f"Error tracking recipe usage for {recipe_id}: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get statistics about both databases"""
        # MySQL count
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT COUNT(*) as count FROM Recipes")
            mysql_count = cursor.fetchone()['count']
        
        # ChromaDB count
        vector_count = self.vector_store.get_recipe_count()
        
        return {
            "mysql_recipes": mysql_count,
            "vector_recipes": vector_count,
            "in_sync": mysql_count == vector_count
        }
