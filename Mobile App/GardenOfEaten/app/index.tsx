import { Text, View, Button } from "react-native";

const userId =  "Hassan"; // Replace with actual user ID

export default function Index() {
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text>Edit app/index.tsx to edit this screen.</Text>
      <Button
        title="Generate Meal Plan"
        onPress={async () => {
          await fetch(`http://192.168.0.39:8000/mealplan/generate/${userId}`, {
            method: "POST"
          });
        }}
      />
    </View>
  );
}
