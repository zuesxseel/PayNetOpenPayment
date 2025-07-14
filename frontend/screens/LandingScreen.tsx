import { View, Text, StyleSheet, ScrollView, SafeAreaView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppButton } from "../components/AppButton"
import { Colors } from "../constants/Colors"

const Feature = ({ icon, title, text }: { icon: any; title: string; text: string }) => (
  <View style={styles.feature}>
    <View style={styles.featureIcon}>
      <Feather name={icon} size={24} color={Colors.primary} />
    </View>
    <Text style={styles.featureTitle}>{title}</Text>
    <Text style={styles.featureText}>{text}</Text>
  </View>
)

export default function LandingScreen({ navigation }: any) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.hero}>
          <Text style={styles.title}>Open Payment</Text>
          <Text style={styles.subtitle}>Seamless Cross-Border Payments. Always On. Even Offline.</Text>
          <Text style={styles.description}>
            Tired of incompatible QRs and network downtime? We offer a single, reliable payment solution for everyone.
          </Text>
          <AppButton title="Try MVP" onPress={() => navigation.navigate("Scan")} />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How we fix it</Text>
          <View style={styles.featuresGrid}>
            <Feature icon="globe" title="Unified QR" text="One QR for all networks." />
            <Feature icon="wifi-off" title="Offline Web3" text="Payments work without internet." />
            <Feature icon="cpu" title="Smart FX" text="AI-powered best rates." />
            <Feature icon="shield" title="AI Security" text="Advanced fraud detection." />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: Colors.background },
  container: { padding: 20, paddingBottom: 50 },
  hero: { alignItems: "center", marginBottom: 40, paddingTop: 40 },
  title: { fontSize: 40, fontWeight: "bold", color: Colors.text, textAlign: "center" },
  subtitle: { fontSize: 22, fontWeight: "600", color: Colors.primary, textAlign: "center", marginVertical: 12 },
  description: { fontSize: 16, color: Colors.textSecondary, textAlign: "center", marginBottom: 24, lineHeight: 24 },
  section: { marginBottom: 30 },
  sectionTitle: { fontSize: 28, fontWeight: "bold", color: Colors.text, marginBottom: 20, textAlign: "center" },
  featuresGrid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  feature: {
    width: "48%",
    alignItems: "center",
    marginBottom: 20,
    backgroundColor: Colors.white,
    padding: 15,
    borderRadius: 16,
  },
  featureIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: Colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  featureTitle: { fontSize: 16, fontWeight: "bold", color: Colors.text, marginBottom: 4 },
  featureText: { fontSize: 13, color: Colors.textSecondary, textAlign: "center" },
})
