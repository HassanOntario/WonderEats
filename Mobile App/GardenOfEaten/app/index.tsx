import { Text, View, Button, ScrollView, ActivityIndicator } from "react-native";
import { useState } from "react";

const userId =  "Hassan"; // Replace with actual user ID

export default function Index() {
  const [mealPlan, setMealPlan] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleGenerateMealPlan = async () => {
    setLoading(true);
    setMealPlan("");
    try {
      const response = await fetch(`http://192.168.0.11:8000/mealplan/generate/${userId}`, {
        method: "POST"
      });
      const data = await response.json();
      console.log("Response:", data);
      setMealPlan(data.meal_plan || JSON.stringify(data, null, 2));
    } catch (error) {
      console.error("Error:", error);
      setMealPlan("Error generating meal plan: " + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 20 }}>
      <View style={{ alignItems: "center", marginVertical: 20 }}>
        <Text style={{ fontSize: 18, marginBottom: 10 }}>Meal Plan Generator</Text>
        <Button
          title="Generate Meal Plan"
          onPress={handleGenerateMealPlan}
          disabled={loading}
        />
      </View>
      
      {loading && <ActivityIndicator size="large" color="#0000ff" />}
      
      {mealPlan && (
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 10 }}>
            Your Meal Plan:
          </Text>
          <Text style={{ fontSize: 14 }}>{mealPlan}</Text>
        </View>
      )}
    </ScrollView>
  );
}
