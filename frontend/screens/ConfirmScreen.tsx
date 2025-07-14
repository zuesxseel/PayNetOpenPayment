import { View, Text, StyleSheet, SafeAreaView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppButton } from "../components/AppButton"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"

const AlertBox = ({ type, title, text }: { type: "warning" | "info"; title: string; text: string }) => {
  const isWarning = type === "warning"
  const bgColor = isWarning ? Colors.dangerLight : Colors.primaryLight
  const iconColor = isWarning ? Colors.danger : Colors.primary
  const iconName = isWarning ? "alert-triangle" : "gift"

  return (
    <View style={[styles.alertBox, { backgroundColor: bgColor }]}>
      <Feather name={iconName} size={24} color={iconColor} style={{ marginRight: 12 }} />
      <View style={{ flex: 1 }}>
        <Text style={[styles.alertTitle, { color: iconColor }]}>{title}</Text>
        <Text style={styles.alertText}>{text}</Text>
      </View>
    </View>
  )
}

export default function ConfirmScreen({ navigation }: any) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Feather name="shield-alert" size={40} color={Colors.danger} />
          <Text style={styles.title}>AI Transaction Summary</Text>
          <Text style={styles.subtitle}>Review risk analysis and offers before confirming.</Text>
        </View>
        <AppCard>
          <AlertBox
            type="warning"
            title="Risk Score: 43 – Medium"
            text="Reason: Location mismatch from typical spending areas."
          />
          <AlertBox
            type="info"
            title="AI-Powered Offer"
            text="Spend RM100 more at FamilyMart today, get RM5 instant cashback!"
          />
        </AppCard>
        <AppButton title="Complete Payment" onPress={() => navigation.navigate("T+ Tree")} />
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: Colors.background },
  container: { flex: 1, justifyContent: "center", padding: 20, gap: 20 },
  header: { alignItems: "center" },
  title: { fontSize: 28, fontWeight: "bold", color: Colors.text, marginTop: 16 },
  subtitle: { fontSize: 16, color: Colors.textSecondary, textAlign: "center", marginTop: 8 },
  alertBox: { flexDirection: "row", alignItems: "center", padding: 16, borderRadius: 12, marginBottom: 16 },
  alertTitle: { fontSize: 16, fontWeight: "bold" },
  alertText: { fontSize: 14, color: Colors.textSecondary, marginTop: 4 },
})
