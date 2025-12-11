"""
Test script to create a user and generate a meal plan
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test user data
test_user = {
    "user": {
        "user_id": "test_user_001",
        "name": "Hassan",
        "age": 25,
        "height_cm": 175,
        "weight_kg": 80,
        "goals": "lose_fat",
        "budget_per_week": 100,
        "scheduling_constraints": "Busy weekdays, free weekends",
        "equipment_available": ["oven", "stove", "microwave", "blender"]
    },
    "nutrition": {
        "bmr": 1800,
        "tdee": 2500,
        "maintenance_calories": 2500,
        "allergies": ["peanuts"],
        "dietary_identities": []
    },
    "preferences": {
        "favorite_cuisines": ["Mediterranean", "Asian"],
        "disliked_ingredients": ["mushrooms", "olives"],
        "meal_frequency": 3,
        "snack_preference": True
    },
    "insights": {
        "cultural_context": "North American",
        "lifestyle_habits": "Active lifestyle, works out 4x per week",
        "health_conditions": [],
        "energy_levels": "Good"
    },
    "fridge_contents": {
        "ingredients_on_hand": ["chicken breast", "eggs", "rice", "broccoli", "milk"]
    }
}

def create_user():
    """Create a test user"""
    print("=" * 60)
    print("1️⃣  Creating test user...")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User created successfully!")
            print(f"   User ID: {result['user_id']}")
            return result['user_id']
        else:
            print(f"❌ Error creating user: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        print("   Start the server with: uvicorn Backend.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def generate_mealplan(user_id):
    """Generate a meal plan for the user"""
    print("\n" + "=" * 60)
    print("2️⃣  Generating meal plan...")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/{user_id}/mealplans",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Meal plan generated successfully!")
            print(f"   Meal Plan ID: {result['meal_plan_id']}")
            print(f"\n📋 Generated Meal Plan:")
            print("=" * 60)
            print(result['meal_plan'])
            print("=" * 60)
            return result
        else:
            print(f"❌ Error generating meal plan: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def get_user(user_id):
    """Get user data to verify it exists"""
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if __name__ == "__main__":
    print("\n🧪 Testing Meal Plan Generation with RAG System")
    print("=" * 60)
    
    # Check if user already exists
    user_id = test_user["user"]["user_id"]
    existing_user = get_user(user_id)
    
    if existing_user:
        print(f"✅ User '{user_id}' already exists")
        print("   Skipping user creation...")
    else:
        # Create user
        created_id = create_user()
        if not created_id:
            print("\n❌ Cannot proceed without a user. Exiting.")
            exit(1)
        user_id = created_id
    
    # Generate meal plan
    result = generate_mealplan(user_id)
    
    if result:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed")
