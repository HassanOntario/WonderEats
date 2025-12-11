-- Create database
CREATE DATABASE IF NOT EXISTS GardenOfEaten;
USE GardenOfEaten;

-- User table
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Age INT NOT NULL,
    Height_cm FLOAT NOT NULL,
    Weight_kg FLOAT NOT NULL,
    Goals JSON NOT NULL,
    Budget_weekly INT NULL,
    Scheduling_constraints JSON NULL,
    Equipment_available JSON NULL
);

-- UserNutritionProfile table
CREATE TABLE IF NOT EXISTS UserNutritionProfile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    BMR FLOAT NOT NULL,
    TDEE FLOAT NOT NULL,
    Maintenance_cals FLOAT NOT NULL,
    Allergies JSON NULL,
    Dietary_identities JSON NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserPreferences table
CREATE TABLE IF NOT EXISTS UserPreferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Favorite_cuisines JSON NULL,
    Disliked_ingredients JSON NULL,
    Meal_frequency INT NOT NULL,
    Snack_preference BOOLEAN NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserInsights table
CREATE TABLE IF NOT EXISTS UserInsights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Cultural_context JSON NULL,
    Lifestyle_habits JSON NULL,
    Health_conditions JSON NULL,
    Energy_levels VARCHAR(255) NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserInsightsHistory table
CREATE TABLE IF NOT EXISTS UserInsightsHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Cultural_context JSON NULL,
    Lifestyle_habits JSON NULL,
    Health_conditions JSON NULL,
    Energy_levels VARCHAR(255) NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserNutritionProfileHistory table
CREATE TABLE IF NOT EXISTS UserNutritionProfileHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    BMR FLOAT NOT NULL,
    TDEE FLOAT NOT NULL,
    Maintenance_cals FLOAT NOT NULL,
    Allergies JSON NULL,
    Dietary_identities JSON NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserPreferencesHistory table
CREATE TABLE IF NOT EXISTS UserPreferencesHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Favorite_cuisines JSON NULL,
    Disliked_ingredients JSON NULL,
    Meal_frequency INT NOT NULL,
    Snack_preference BOOLEAN NULL,
    User_id INT NOT NULL,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserFridgeContents table
CREATE TABLE IF NOT EXISTS UserFridgeContents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Ingredients_on_hand JSON NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

-- UserFridgeContentsHistory table
CREATE TABLE IF NOT EXISTS UserFridgeContentsHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Ingredients_on_hand JSON NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

-- MealPlanHistory table
CREATE TABLE IF NOT EXISTS MealPlanHistory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    User_id INT NOT NULL,
    Generated_meals JSON NULL,
    Ingredients_used JSON NULL,
    User_feedback JSON NULL,
    Energy_levels VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_id) REFERENCES User(id) ON DELETE CASCADE
);

-- Recipes table (for imported recipes from APIs)
CREATE TABLE IF NOT EXISTS Recipes (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(100) NOT NULL, -- 'spoonacular', 'edamam', 'user_generated'
    cuisine VARCHAR(100),
    description TEXT,
    nutrition JSON NOT NULL,
    ingredients JSON NOT NULL,
    instructions TEXT,
    tags JSON,
    popularity_score INT DEFAULT 0,
    created_by INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES User(id) ON DELETE SET NULL
);

-- RecipeUsage table (track which recipes were used in meal plans)
CREATE TABLE IF NOT EXISTS RecipeUsage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    meal_plan_id BIGINT NOT NULL,
    recipe_id VARCHAR(255) NOT NULL,
    user_rating VARCHAR(50), -- 'liked', 'disliked', 'neutral'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_plan_id) REFERENCES MealPlanHistory(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES Recipes(id) ON DELETE CASCADE
);
