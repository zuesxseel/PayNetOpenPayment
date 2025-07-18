"use client"

import { useState } from "react"
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, Switch, Alert } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"

interface PaymentCard {
  id: string
  type: "debit" | "credit"
  bank: string
  lastFour: string
  expiryDate: string
  isDefault: boolean
  isActive: boolean
}

interface TrustedDevice {
  id: string
  name: string
  type: "mobile" | "desktop" | "tablet"
  lastUsed: string
  isCurrentDevice: boolean
  zkpEnabled: boolean
}

interface DuitNowAccount {
  phoneNumber: string
  nric: string
  email: string
  walletId: string
  isVerified: boolean
}

const AccountDetailsScreen = ({ navigation }: any) => {
  const [duitNowAccount] = useState<DuitNowAccount>({
    phoneNumber: "+60 12-345-6789",
    nric: "123456-78-9012",
    email: "asthon.hall@email.com",
    walletId: "WLT-MY-2024-789456",
    isVerified: true,
  })

  const [paymentCards, setPaymentCards] = useState<PaymentCard[]>([
    {
      id: "1",
      type: "debit",
      bank: "Maybank",
      lastFour: "4567",
      expiryDate: "12/26",
      isDefault: true,
      isActive: true,
    },
    {
      id: "2",
      type: "credit",
      bank: "CIMB",
      lastFour: "8901",
      expiryDate: "08/27",
      isDefault: false,
      isActive: true,
    },
    {
      id: "3",
      type: "debit",
      bank: "Public Bank",
      lastFour: "2345",
      expiryDate: "03/25",
      isDefault: false,
      isActive: false,
    },
  ])

  const [trustedDevices, setTrustedDevices] = useState<TrustedDevice[]>([
    {
      id: "1",
      name: "iPhone 15 Pro",
      type: "mobile",
      lastUsed: "Now",
      isCurrentDevice: true,
      zkpEnabled: true,
    },
    {
      id: "2",
      name: "MacBook Pro",
      type: "desktop",
      lastUsed: "2 hours ago",
      isCurrentDevice: false,
      zkpEnabled: true,
    },
    {
      id: "3",
      name: "Unknown Device (Chrome)",
      type: "desktop",
      lastUsed: "3 days ago",
      isCurrentDevice: false,
      zkpEnabled: false,
    },
  ])

  const [zkpGlobalEnabled, setZkpGlobalEnabled] = useState(true)
  const [autoBlockEnabled, setAutoBlockEnabled] = useState(true)
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)

  const toggleCardStatus = (cardId: string) => {
    setPaymentCards((cards) => cards.map((card) => (card.id === cardId ? { ...card, isActive: !card.isActive } : card)))
  }

  const setDefaultCard = (cardId: string) => {
    setPaymentCards((cards) =>
      cards.map((card) => ({
        ...card,
        isDefault: card.id === cardId,
      })),
    )
  }

  const removeCard = (cardId: string) => {
    Alert.alert("Remove Card", "Are you sure you want to remove this payment card?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Remove",
        style: "destructive",
        onPress: () => {
          setPaymentCards((cards) => cards.filter((card) => card.id !== cardId))
        },
      },
    ])
  }

  const toggleDeviceTrust = (deviceId: string) => {
    setTrustedDevices((devices) =>
      devices.map((device) => (device.id === deviceId ? { ...device, zkpEnabled: !device.zkpEnabled } : device)),
    )
  }

  const removeDevice = (deviceId: string) => {
    Alert.alert("Remove Device", "This device will no longer be trusted for transactions.", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Remove",
        style: "destructive",
        onPress: () => {
          setTrustedDevices((devices) => devices.filter((device) => device.id !== deviceId))
        },
      },
    ])
  }

  const addNewCard = () => {
    Alert.alert("Add New Card", "This feature will open your bank's secure card linking process.")
  }

  const renderDuitNowSection = () => (
    <AppCard style={styles.sectionCard}>
      <View style={styles.sectionHeader}>
        <Feather name="smartphone" size={24} color={Colors.primary} />
        <Text style={styles.sectionTitle}>DuitNow Account</Text>
        {duitNowAccount.isVerified && <Feather name="check-circle" size={20} color={Colors.success} />}
      </View>

      <View style={styles.accountInfo}>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Phone Number:</Text>
          <Text style={styles.infoValue}>{duitNowAccount.phoneNumber}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>NRIC:</Text>
          <Text style={styles.infoValue}>{duitNowAccount.nric}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Email:</Text>
          <Text style={styles.infoValue}>{duitNowAccount.email}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Wallet ID:</Text>
          <Text style={[styles.infoValue, styles.walletId]}>{duitNowAccount.walletId}</Text>
        </View>
      </View>

      <View style={styles.verificationBadge}>
        <Text style={styles.verificationText}>Verified Account</Text>
      </View>
    </AppCard>
  )

  const renderPaymentCardsSection = () => (
    <AppCard style={styles.sectionCard}>
      <View style={styles.sectionHeader}>
        <Feather name="credit-card" size={24} color={Colors.primary} />
        <Text style={styles.sectionTitle}>Linked Payment Cards</Text>
        <TouchableOpacity onPress={addNewCard} style={styles.addButton}>
          <Feather name="plus" size={20} color={Colors.primary} />
        </TouchableOpacity>
      </View>

      {paymentCards.map((card) => (
        <View key={card.id} style={[styles.cardItem, !card.isActive && styles.inactiveCard]}>
          <View style={styles.cardInfo}>
            <View style={styles.cardHeader}>
              <View style={styles.cardTypeContainer}>
                <Feather
                  name="credit-card"
                  size={20}
                  color={card.isActive ? Colors.primary : Colors.textSecondary}
                />
                <Text style={[styles.cardType, !card.isActive && styles.inactiveText]}>{card.type.toUpperCase()}</Text>
                {card.isDefault && (
                  <View style={styles.defaultBadge}>
                    <Text style={styles.defaultText}>DEFAULT</Text>
                  </View>
                )}
              </View>
              <Switch
                value={card.isActive}
                onValueChange={() => toggleCardStatus(card.id)}
                trackColor={{ false: Colors.border, true: Colors.primaryLight }}
                thumbColor={card.isActive ? Colors.primary : Colors.textSecondary}
              />
            </View>

            <Text style={[styles.cardDetails, !card.isActive && styles.inactiveText]}>
              {card.bank} •••• {card.lastFour}
            </Text>
            <Text style={[styles.cardExpiry, !card.isActive && styles.inactiveText]}>Expires: {card.expiryDate}</Text>

            <View style={styles.cardActions}>
              {!card.isDefault && card.isActive && (
                <TouchableOpacity onPress={() => setDefaultCard(card.id)} style={styles.actionButton}>
                  <Text style={styles.actionButtonText}>Set as Default</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity onPress={() => removeCard(card.id)} style={styles.removeButton}>
                <Text style={styles.removeButtonText}>Remove</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ))}
    </AppCard>
  )

  const renderTrustedDevicesSection = () => (
    <AppCard style={styles.sectionCard}>
      <View style={styles.sectionHeader}>
        <Feather name="shield" size={24} color={Colors.primary} />
        <Text style={styles.sectionTitle}>Trusted Devices & ZKP Security</Text>
      </View>

      <View style={styles.securityInfo}>
        <Text style={styles.securityDescription}>
          Devices marked as "Trusted" can make payments without additional verification. Untrusted devices will trigger
          Zero-Knowledge Proof (ZKP) checks for enhanced security.
        </Text>
      </View>

      {trustedDevices.map((device) => (
        <View key={device.id} style={[styles.deviceItem, device.isCurrentDevice && styles.currentDevice]}>
          <View style={styles.deviceInfo}>
            <View style={styles.deviceHeader}>
              <Feather
                name={device.type === "mobile" ? "smartphone" : device.type === "tablet" ? "tablet" : "monitor"}
                size={20}
                color={device.zkpEnabled ? Colors.primary : Colors.textSecondary}
              />
              <Text style={styles.deviceName}>{device.name}</Text>
              {device.isCurrentDevice && (
                <View style={styles.currentBadge}>
                  <Text style={styles.currentText}>CURRENT</Text>
                </View>
              )}
            </View>

            <Text style={styles.deviceLastUsed}>Last used: {device.lastUsed}</Text>

            <View style={styles.deviceControls}>
              <View style={styles.trustControl}>
                <Text style={styles.trustLabel}>Trusted Device:</Text>
                <Switch
                  value={device.zkpEnabled}
                  onValueChange={() => toggleDeviceTrust(device.id)}
                  trackColor={{ false: Colors.border, true: Colors.successLight }}
                  thumbColor={device.zkpEnabled ? Colors.success : Colors.textSecondary}
                />
              </View>

              {!device.isCurrentDevice && (
                <TouchableOpacity onPress={() => removeDevice(device.id)} style={styles.removeDeviceButton}>
                  <Feather name="trash-2" size={16} color={Colors.danger} />
                  <Text style={styles.removeDeviceText}>Remove</Text>
                </TouchableOpacity>
              )}
            </View>

            <View style={styles.zkpStatus}>
              <Feather
                name={device.zkpEnabled ? "check-circle" : "alert-triangle"}
                size={16}
                color={device.zkpEnabled ? Colors.success : Colors.warning}
              />
              <Text style={[styles.zkpStatusText, { color: device.zkpEnabled ? Colors.success : Colors.warning }]}>
                {device.zkpEnabled
                  ? "ZKP verification enabled - transactions approved instantly"
                  : "ZKP verification required - additional security checks will apply"}
              </Text>
            </View>
          </View>
        </View>
      ))}
    </AppCard>
  )

  const renderSecuritySettingsSection = () => (
    <AppCard style={styles.sectionCard}>
      <View style={styles.sectionHeader}>
        <Feather name="settings" size={24} color={Colors.primary} />
        <Text style={styles.sectionTitle}>Security Preferences</Text>
      </View>

      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>Global ZKP Protection</Text>
          <Text style={styles.settingDescription}>
            Enable Zero-Knowledge Proof verification for all untrusted devices
          </Text>
        </View>
        <Switch
          value={zkpGlobalEnabled}
          onValueChange={setZkpGlobalEnabled}
          trackColor={{ false: Colors.border, true: Colors.primaryLight }}
          thumbColor={zkpGlobalEnabled ? Colors.primary : Colors.textSecondary}
        />
      </View>

      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>Auto-Block Suspicious Transactions</Text>
          <Text style={styles.settingDescription}>Automatically block payments when ZKP verification fails</Text>
        </View>
        <Switch
          value={autoBlockEnabled}
          onValueChange={setAutoBlockEnabled}
          trackColor={{ false: Colors.border, true: Colors.dangerLight }}
          thumbColor={autoBlockEnabled ? Colors.danger : Colors.textSecondary}
        />
      </View>

      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>Security Notifications</Text>
          <Text style={styles.settingDescription}>Receive alerts for blocked transactions and security events</Text>
        </View>
        <Switch
          value={notificationsEnabled}
          onValueChange={setNotificationsEnabled}
          trackColor={{ false: Colors.border, true: Colors.successLight }}
          thumbColor={notificationsEnabled ? Colors.success : Colors.textSecondary}
        />
      </View>

      <View style={styles.securitySummary}>
        <Feather name="info" size={16} color={Colors.primary} />
        <Text style={styles.securitySummaryText}>
          When you make online payments from untrusted devices, our ZKP system will verify your identity using biometric
          data and behavioral patterns. Failed verification will result in transaction blocking and fraud alerts.
        </Text>
      </View>
    </AppCard>
  )

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Feather name="arrow-left" size={24} color={Colors.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Account Details</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {renderDuitNowSection()}
        {renderPaymentCardsSection()}
        {renderTrustedDevicesSection()}
        {renderSecuritySettingsSection()}

        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: Colors.text,
  },
  headerRight: {
    width: 32,
  },
  scrollContainer: {
    flex: 1,
    padding: 20,
  },
  sectionCard: {
    marginBottom: 20,
    padding: 20,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: Colors.text,
    marginLeft: 12,
    flex: 1,
  },
  addButton: {
    padding: 4,
  },
  accountInfo: {
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  infoLabel: {
    fontSize: 14,
    color: Colors.textSecondary,
    fontWeight: "500",
  },
  infoValue: {
    fontSize: 14,
    color: Colors.text,
    fontWeight: "600",
  },
  walletId: {
    fontFamily: "monospace",
    fontSize: 12,
  },
  verificationBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.successLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: "flex-start",
  },
  verificationText: {
    fontSize: 12,
    color: Colors.success,
    fontWeight: "600",
    marginLeft: 6,
  },
  cardItem: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    backgroundColor: Colors.white,
  },
  inactiveCard: {
    backgroundColor: Colors.backgroundLight,
    opacity: 0.7,
  },
  cardInfo: {
    flex: 1,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  cardTypeContainer: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  cardType: {
    fontSize: 14,
    fontWeight: "bold",
    color: Colors.text,
    marginLeft: 8,
  },
  inactiveText: {
    color: Colors.textSecondary,
  },
  defaultBadge: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginLeft: 8,
  },
  defaultText: {
    fontSize: 10,
    color: Colors.primary,
    fontWeight: "bold",
  },
  cardDetails: {
    fontSize: 16,
    color: Colors.text,
    fontWeight: "600",
    marginBottom: 4,
  },
  cardExpiry: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 12,
  },
  cardActions: {
    flexDirection: "row",
    gap: 12,
  },
  actionButton: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  actionButtonText: {
    fontSize: 12,
    color: Colors.primary,
    fontWeight: "600",
  },
  removeButton: {
    backgroundColor: Colors.dangerLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  removeButtonText: {
    fontSize: 12,
    color: Colors.danger,
    fontWeight: "600",
  },
  securityInfo: {
    backgroundColor: Colors.primaryLight,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  securityDescription: {
    fontSize: 14,
    color: Colors.primary,
    lineHeight: 20,
  },
  deviceItem: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    backgroundColor: Colors.white,
  },
  currentDevice: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primaryLight,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginLeft: 12,
    flex: 1,
  },
  currentBadge: {
    backgroundColor: Colors.primary,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  currentText: {
    fontSize: 10,
    color: Colors.white,
    fontWeight: "bold",
  },
  deviceLastUsed: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 12,
  },
  deviceControls: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  trustControl: {
    flexDirection: "row",
    alignItems: "center",
  },
  trustLabel: {
    fontSize: 14,
    color: Colors.text,
    marginRight: 12,
  },
  removeDeviceButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.dangerLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  removeDeviceText: {
    fontSize: 12,
    color: Colors.danger,
    fontWeight: "600",
    marginLeft: 4,
  },
  zkpStatus: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: Colors.backgroundLight,
    padding: 12,
    borderRadius: 8,
  },
  zkpStatusText: {
    fontSize: 12,
    marginLeft: 8,
    flex: 1,
    lineHeight: 16,
  },
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 16,
  },
  securitySummary: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: Colors.backgroundLight,
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
  },
  securitySummaryText: {
    fontSize: 14,
    color: Colors.text,
    marginLeft: 12,
    flex: 1,
    lineHeight: 20,
  },
  bottomSpacing: {
    height: 40,
  },
})

export default AccountDetailsScreen
