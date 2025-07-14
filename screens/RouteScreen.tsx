import { View, Text, StyleSheet, SafeAreaView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppButton } from "../components/AppButton"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"

const InfoRow = ({ label, value, icon }: { label: string; value: string; icon: any }) => (
  <View style={styles.infoRow}>
    <View style={{ flexDirection: "row", alignItems: "center" }}>
      <Feather name={icon} size={20} color={Colors.primary} style={{ marginRight: 12 }} />
      <Text style={styles.infoLabel}>{label}</Text>
    </View>
    <Text style={styles.infoValue}>{value}</Text>
  </View>
)

export default function RouteScreen({ route, navigation }: any) {
  const { payload } = route.params
  let qrType = "Unknown"
  try {
    if (payload) qrType = JSON.parse(decodeURIComponent(payload)).type || "Unknown"
  } catch (e) {}

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Feather name="cpu" size={40} color={Colors.secondary} />
          <Text style={styles.title}>Smart Routing</Text>
          <Text style={styles.subtitle}>We found the most optimal route for your payment.</Text>
        </View>
        <AppCard>
          <View style={styles.savingsBanner}>
            <Feather name="sparkles" size={22} color={Colors.secondary} />
            <Text style={styles.savingsText}>You saved RM4.12 via Smart FX Routing!</Text>
          </View>
          <InfoRow label="Detected QR Source" value={qrType} icon="compass" />
          <InfoRow label="Selected Network" value="UPI → DuitNow" icon="git-pull-request" />
          <InfoRow label="Face Auth" value="Verified" icon="check-circle" />
        </AppCard>
        <View style={styles.buttonContainer}>
          <AppButton title="Go Offline?" onPress={() => navigation.navigate("Offline")} variant="outline" />
          <AppButton title="Next" onPress={() => navigation.navigate("Confirm")} />
        </View>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: Colors.background },
  container: { flex: 1, justifyContent: "center", padding: 20 },
  header: { alignItems: "center", marginBottom: 30 },
  title: { fontSize: 28, fontWeight: "bold", color: Colors.text, marginTop: 16 },
  subtitle: { fontSize: 16, color: Colors.textSecondary, textAlign: "center", marginTop: 8 },
  savingsBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.secondaryLight,
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  savingsText: { fontSize: 16, fontWeight: "600", color: Colors.secondary, marginLeft: 12 },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  infoLabel: { fontSize: 16, color: Colors.textSecondary },
  infoValue: { fontSize: 16, fontWeight: "600", color: Colors.text },
  buttonContainer: { marginTop: 30, flexDirection: "row", justifyContent: "space-between", gap: 10 },
})
