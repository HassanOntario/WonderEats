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
