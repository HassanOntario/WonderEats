import asyncio
import sys
from Backend.Routers.recipe_repo import RecipeRepository
from Backend.Services.recipe_embedder import RecipeVectorStore

async def seed_recipe_database(user_goal: str = "lose_fat"):
    """
    One-time script to populate recipe database
    Writes to BOTH MySQL and ChromaDB vector database
    
    Args:
        user_goal: The user's selected goal ('lose_fat', 'gain_muscle', or 'maintain')
    
    If vector DB is empty:
    - Fetch 50 recipes for the user's selected goal
    - Fetch 50 recipes tagged with 'maintain' goal (for flexibility)
    
    If vector DB has data:
    - Run full seed across all goals and cuisines
    """
    repo = RecipeRepository()
    vector_store = RecipeVectorStore()
    
    # Validate user goal
    valid_goals = ["lose_fat", "gain_muscle", "maintain"]
    if user_goal not in valid_goals:
        print(f"❌ Invalid goal '{user_goal}'. Must be one of: {', '.join(valid_goals)}")
        return
    
    # Check if vector database is empty
    if vector_store.is_empty():
        print("📦 Vector database is empty. Starting initial seed...")
        print(f"🎯 User goal: {user_goal}")
        print("=" * 60)
        
        # Seed with user's selected goal
        print(f"\n  Fetching 50 '{user_goal}' recipes...")
        result1 = await repo.seed_from_apis(
            goal=user_goal,
            cuisine=None,
            limit=50
        )
        print(f"   ✅ Imported: {result1['imported']}, MySQL: {result1['saved_mysql']}, Vector: {result1['saved_vector']}")
        
        await asyncio.sleep(2)  # Rate limiting
        
        # Seed with maintain recipes (unless that's already the user's goal)
        if user_goal != "maintain":
            print("\n  Fetching 50 'maintain' recipes (for flexibility)...")
            result2 = await repo.seed_from_apis(
                goal="maintain",
                cuisine=None,
                limit=50
            )
            print(f"   ✅ Imported: {result2['imported']}, MySQL: {result2['saved_mysql']}, Vector: {result2['saved_vector']}")
            total_imported = result1['imported'] + result2['imported']
        else:
            print("\n  User goal is 'maintain', fetching additional variety...")
            result2 = await repo.seed_from_apis(
                goal="maintain",
                cuisine="Mediterranean",  # Add variety with a specific cuisine
                limit=50
            )
            print(f"   ✅ Imported: {result2['imported']}, MySQL: {result2['saved_mysql']}, Vector: {result2['saved_vector']}")
            total_imported = result1['imported'] + result2['imported']
        
        print("\n" + "=" * 60)
        print(f"✅ Initial seed complete! Total recipes: {total_imported}")
        
    else:
        print(f"📊 Vector database already has {vector_store.get_recipe_count()} recipes")
        print("Running full seed across all goals and cuisines...")
        print("=" * 60)
        
        goals = ["lose_fat", "gain_muscle", "maintain"]
        cuisines = ["Mediterranean", "Asian", "Mexican", "Italian", "American", None]
        
        total_imported = 0
        
        for goal in goals:
            for cuisine in cuisines:
                cuisine_name = cuisine or 'all'
                print(f"\n📥 Fetching {goal} recipes from {cuisine_name} cuisine...")
                
                result = await repo.seed_from_apis(
                    goal=goal,
                    cuisine=cuisine,
                    limit=20
                )
                
                total_imported += result['imported']
                print(f"   ✅ Imported: {result['imported']}, MySQL: {result['saved_mysql']}, Vector: {result['saved_vector']}")
                
                await asyncio.sleep(1)  # Rate limiting
        
        print("\n" + "=" * 60)
        print(f"✅ Full seed complete! Total new recipes: {total_imported}")
    
    # Show final statistics
    print("\n📊 Database Statistics:")
    stats = repo.get_database_stats()
    print(f"   MySQL recipes: {stats['mysql_recipes']}")
    print(f"   Vector recipes: {stats['vector_recipes']}")
    print(f"   Databases in sync: {'✅ Yes' if stats['in_sync'] else '❌ No'}")

if __name__ == "__main__":
    # Allow passing user goal as command line argument
    # Usage: python -m Backend.seedRecipeDatabase [lose_fat|gain_muscle|maintain]
    user_goal = sys.argv[1] if len(sys.argv) > 1 else "lose_fat"
    asyncio.run(seed_recipe_database(user_goal))