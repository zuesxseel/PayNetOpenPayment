import { View, Text, StyleSheet, SafeAreaView } from "react-native"
import { Feather } from "@expo/vector-icons"
import Svg, { Path, Circle } from "react-native-svg"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"
import { AppButton } from "../components/AppButton"

const Stat = ({ icon, label, value }: { icon: any; label: string; value: string }) => (
  <View style={styles.stat}>
    <Feather name={icon} size={20} color={Colors.textSecondary} />
    <Text style={styles.statLabel}>{label}</Text>
    <Text style={styles.statValue}>{value}</Text>
  </View>
)

export default function TreeScreen() {
  const progress = 32 // 32%

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Feather name="git-merge" size={40} color={Colors.secondary} />
          <Text style={styles.title}>Grow a Tree</Text>
          <Text style={styles.subtitle}>Instead of earning interest, you help the planet.</Text>
        </View>
        <AppCard>
          <View style={styles.treeContainer}>
            <Svg height="150" width="150" viewBox="0 0 100 100">
              <Path d="M 50 95 V 60" stroke={Colors.textSecondary} strokeWidth="5" />
              <Circle cx="50" cy="40" r={progress * 0.4} fill={Colors.secondary} />
              <Circle cx="35" cy="55" r={progress * 0.3} fill={Colors.secondary} opacity="0.8" />
              <Circle cx="65" cy="55" r={progress * 0.3} fill={Colors.secondary} opacity="0.8" />
            </Svg>
            <View style={styles.progressBar}>
              <View style={[styles.progress, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>Your tree will sprout at RM10 earned.</Text>
          </View>
          <View style={styles.statsContainer}>
            <Stat icon="dollar-sign" label="Earned" value="RM 0.32" />
            <Stat icon="trending-up" label="Progress" value={`${progress}%`} />
            <Stat icon="clock" label="Full Growth" value="22 days" />
          </View>
        </AppCard>
        <AppButton title="View Your Forest" onPress={() => {}} variant="secondary" />
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
  treeContainer: { alignItems: "center", marginBottom: 20 },
  progressBar: {
    width: "80%",
    height: 8,
    backgroundColor: Colors.border,
    borderRadius: 4,
    marginTop: 16,
    overflow: "hidden",
  },
  progress: { height: "100%", backgroundColor: Colors.secondary, borderRadius: 4 },
  progressText: { marginTop: 8, color: Colors.textSecondary, fontSize: 13 },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: 20,
  },
  stat: { alignItems: "center" },
  statLabel: { color: Colors.textSecondary, fontSize: 14, marginTop: 4 },
  statValue: { color: Colors.text, fontSize: 18, fontWeight: "600", marginTop: 2 },
})
