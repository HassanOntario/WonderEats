import httpx
import os
from typing import List, Dict

class RecipeImporter:
    def __init__(self):
        self.spoonacular_key = os.getenv("SPOONACULAR_API_KEY")
        self.edamam_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_key = os.getenv("EDAMAM_APP_KEY")
    
    async def fetch_recipes_by_goal(self, goal: str, cuisine: str = None, limit: int = 50) -> List[Dict]:
        """Fetch recipes optimized for specific fitness goals"""
        
        recipes = []
        
        # Define nutrition targets by goal
        nutrition_params = self._get_nutrition_params(goal)
        
        # Fetch from Spoonacular (better nutrition filtering)
        spoonacular_recipes = await self._fetch_spoonacular(
            cuisine=cuisine,
            nutrition_params=nutrition_params,
            limit=limit // 2
        )
        recipes.extend(spoonacular_recipes)
        
        # Fetch from Edamam (more variety)
        edamam_recipes = await self._fetch_edamam(
            cuisine=cuisine,
            goal=goal,
            limit=limit // 2
        )
        recipes.extend(edamam_recipes)
        
        return self._normalize_recipes(recipes)
    
    def _get_nutrition_params(self, goal: str) -> Dict:
        """Get nutrition parameters for each goal"""
        params = {
            "lose_fat": {
                "maxCalories": 500,
                "minProtein": 25,
                "maxCarbs": 50
            },
            "gain_muscle": {
                "minCalories": 400,
                "minProtein": 35,
                "minCarbs": 40
            },
            "maintain": {
                "minCalories": 300,
                "maxCalories": 600,
                "minProtein": 20
            }
        }
        return params.get(goal, params["maintain"])
    
    async def _fetch_spoonacular(self, cuisine: str, nutrition_params: Dict, limit: int) -> List[Dict]:
        """Fetch from Spoonacular with nutrition filters"""
        async with httpx.AsyncClient() as client:
            params = {
                "apiKey": self.spoonacular_key,
                "number": limit,
                "addRecipeNutrition": True,
                "fillIngredients": True,
                **nutrition_params
            }
            
            if cuisine:
                params["cuisine"] = cuisine
            
            response = await client.get(
                "https://api.spoonacular.com/recipes/complexSearch",
                params=params,
                timeout=30.0
            )
            
            data = response.json()
            return data.get("results", [])
    
    async def _fetch_edamam(self, cuisine: str, goal: str, limit: int) -> List[Dict]:
        """Fetch from Edamam"""
        async with httpx.AsyncClient() as client:
            params = {
                "app_id": self.edamam_id,
                "app_key": self.edamam_key,
                "type": "public",
                "to": limit
            }
            
            # Map goal to Edamam diet labels
            diet_map = {
                "lose_fat": "low-carb",
                "gain_muscle": "high-protein",
                "maintain": "balanced"
            }
            
            if goal in diet_map:
                params["diet"] = diet_map[goal]
            
            if cuisine:
                params["cuisineType"] = cuisine.lower()
            
            response = await client.get(
                "https://api.edamam.com/api/recipes/v2",
                params=params,
                timeout=30.0
            )
            
            data = response.json()
            return [hit["recipe"] for hit in data.get("hits", [])]
    
    def _normalize_recipes(self, recipes: List[Dict]) -> List[Dict]:
        """Normalize recipes from different APIs to unified format"""
        normalized = []
        
        for recipe in recipes:
            # Detect source
            if "spoonacularSourceUrl" in recipe or "id" in recipe:
                normalized.append(self._normalize_spoonacular(recipe))
            elif "uri" in recipe:
                normalized.append(self._normalize_edamam(recipe))
        
        return normalized
    
    def _normalize_spoonacular(self, recipe: Dict) -> Dict:
        """Normalize Spoonacular recipe"""
        nutrition = recipe.get("nutrition", {}).get("nutrients", [])
        
        return {
            "id": f"spoon_{recipe['id']}",
            "name": recipe.get("title", ""),
            "source": "spoonacular",
            "cuisine": recipe.get("cuisines", ["General"])[0] if recipe.get("cuisines") else "General",
            "description": recipe.get("summary", "")[:500],
            "ingredients": [ing.get("name", "") for ing in recipe.get("extendedIngredients", [])],
            "instructions": recipe.get("instructions", ""),
            "nutrition": {
                "calories": next((n["amount"] for n in nutrition if n["name"] == "Calories"), 0),
                "protein": next((n["amount"] for n in nutrition if n["name"] == "Protein"), 0),
                "carbs": next((n["amount"] for n in nutrition if n["name"] == "Carbohydrates"), 0),
                "fat": next((n["amount"] for n in nutrition if n["name"] == "Fat"), 0)
            },
            "tags": self._extract_tags_spoonacular(recipe)
        }
    
    def _normalize_edamam(self, recipe: Dict) -> Dict:
        """Normalize Edamam recipe"""
        nutrients = recipe.get("totalNutrients", {})
        
        return {
            "id": f"edamam_{hash(recipe['uri'])}",
            "name": recipe.get("label", ""),
            "source": "edamam",
            "cuisine": recipe.get("cuisineType", ["General"])[0] if recipe.get("cuisineType") else "General",
            "description": f"{recipe.get('dishType', [''])[0]} from {recipe.get('source', '')}",
            "ingredients": [ing.get("food", "") for ing in recipe.get("ingredients", [])],
            "instructions": recipe.get("url", ""),  # Edamam provides external links
            "nutrition": {
                "calories": nutrients.get("ENERC_KCAL", {}).get("quantity", 0),
                "protein": nutrients.get("PROCNT", {}).get("quantity", 0),
                "carbs": nutrients.get("CHOCDF", {}).get("quantity", 0),
                "fat": nutrients.get("FAT", {}).get("quantity", 0)
            },
            "tags": recipe.get("healthLabels", []) + recipe.get("dietLabels", [])
        }
    
    def _extract_tags_spoonacular(self, recipe: Dict) -> List[str]:
        """Extract tags from Spoonacular recipe"""
        tags = []
        
        # Add diet tags
        if recipe.get("vegetarian"):
            tags.append("vegetarian")
        if recipe.get("vegan"):
            tags.append("vegan")
        if recipe.get("glutenFree"):
            tags.append("gluten-free")
        
        # Add nutrition-based tags
        nutrition = recipe.get("nutrition", {}).get("nutrients", [])
        protein = next((n["amount"] for n in nutrition if n["name"] == "Protein"), 0)
        carbs = next((n["amount"] for n in nutrition if n["name"] == "Carbohydrates"), 0)
        
        if protein > 30:
            tags.append("high-protein")
        if carbs < 30:
            tags.append("low-carb")
        
        return tags