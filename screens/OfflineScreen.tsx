"use client"

import { useState } from "react"
import { View, Text, StyleSheet, Switch, SafeAreaView, ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppButton } from "../components/AppButton"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"

export default function OfflineScreen({ navigation }: any) {
  const [isOffline, setIsOffline] = useState(false)
  const signedVoucher = {
    version: "1.0",
    transactionId: "txn_offline_c4a3b2",
    amount: 55.5,
    signature: "a1b2c3d4e5f6...",
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Feather
            name={isOffline ? "wifi-off" : "wifi"}
            size={40}
            color={isOffline ? Colors.warning : Colors.primary}
          />
          <Text style={styles.title}>Offline Fallback</Text>
          <Text style={styles.subtitle}>Simulate a network outage and see our Web3 voucher system in action.</Text>
        </View>
        <AppCard>
          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Offline Mode</Text>
            <Switch
              trackColor={{ false: Colors.border, true: Colors.warningLight }}
              thumbColor={isOffline ? Colors.warning : Colors.white}
              onValueChange={setIsOffline}
              value={isOffline}
            />
          </View>
          {isOffline && (
            <View style={styles.voucherContainer}>
              <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 10 }}>
                <Feather name="shield" size={20} color={Colors.secondary} />
                <Text style={styles.voucherTitle}>Signed Voucher Preview</Text>
              </View>
              <ScrollView style={styles.codeBlock}>
                <Text style={styles.codeText}>{JSON.stringify(signedVoucher, null, 2)}</Text>
              </ScrollView>
              <Text style={styles.voucherInfo}>Your payment is signed and will settle when you're back online.</Text>
            </View>
          )}
        </AppCard>
        <AppButton title="Go Back Online" onPress={() => navigation.navigate("Confirm")} />
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
  switchContainer: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 10 },
  switchLabel: { fontSize: 18, fontWeight: "500", color: Colors.text },
  voucherContainer: { marginTop: 20, borderTopWidth: 1, borderTopColor: Colors.border, paddingTop: 20 },
  voucherTitle: { fontSize: 16, fontWeight: "600", color: Colors.text, marginLeft: 8 },
  codeBlock: { backgroundColor: Colors.background, padding: 12, borderRadius: 8, maxHeight: 150 },
  codeText: { fontFamily: "monospace", fontSize: 12, color: Colors.textSecondary },
  voucherInfo: { textAlign: "center", marginTop: 16, color: Colors.textSecondary, fontSize: 14 },
})
