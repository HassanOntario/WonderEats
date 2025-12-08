import asyncio
from Backend.Services.recipe_importer import RecipeImporter
from Backend.Services.recipe_embedder import RecipeVectorStore

async def seed_recipe_database():
    """One-time script to populate recipe database"""
    importer = RecipeImporter()
    vector_store = RecipeVectorStore()
    
    goals = ["lose_fat", "gain_muscle", "maintain"]
    cuisines = ["Mediterranean", "Asian", "Mexican", "Italian", "American", None]
    
    all_recipes = []
    
    for goal in goals:
        for cuisine in cuisines:
            print(f"Fetching {goal} recipes from {cuisine or 'all'} cuisine...")
            recipes = await importer.fetch_recipes_by_goal(
                goal=goal,
                cuisine=cuisine,
                limit=20  # 3 goals × 6 cuisines × 20 = 360 recipes
            )
            all_recipes.extend(recipes)
            await asyncio.sleep(1)  # Rate limiting
    
    # Remove duplicates
    unique_recipes = {r["id"]: r for r in all_recipes}.values()
    
    print(f"\nImported {len(unique_recipes)} unique recipes")
    print("Adding to vector database...")
    
    vector_store.add_recipes(list(unique_recipes))
    
    print("✅ Recipe database seeded successfully!")
    
    # Show summary
    for goal in goals:
        count = sum(1 for r in unique_recipes if goal in str(r))
        print(f"  {goal}: ~{count} recipes")

if __name__ == "__main__":
    asyncio.run(seed_recipe_database())