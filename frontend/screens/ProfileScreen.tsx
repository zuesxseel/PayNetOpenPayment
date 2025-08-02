"use client"

import { useState } from "react"
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, Image } from "react-native"
import { Feather } from "@expo/vector-icons"
import { AppCard } from "../components/AppCard"
import { Colors } from "../constants/Colors"
import { useAuth } from "../context/AuthContext"

const ProfileOption = ({ icon, title, subtitle, onPress, showBadge = false }) => (
  <TouchableOpacity onPress={onPress} style={styles.profileOption}>
    <View style={styles.optionLeft}>
      <View style={styles.iconContainer}>
        <Feather name={icon} size={20} color={Colors.primary} />
      </View>
      <View style={styles.optionText}>
        <Text style={styles.optionTitle}>{title}</Text>
        {subtitle && <Text style={styles.optionSubtitle}>{subtitle}</Text>}
      </View>
    </View>
    <View style={styles.optionRight}>
      {showBadge && (
        <View style={styles.notificationBadge}>
          <Text style={styles.badgeText}>!</Text>
        </View>
      )}
      <Feather name="chevron-right" size={20} color={Colors.textSecondary} />
    </View>
  </TouchableOpacity>
)

export default function ProfileScreen({ navigation }: any) {
  const { logout } = useAuth()
  const [userProfile] = useState({
    name: "Ng Hui Siang",
    email: "huisiang0102@gmail.com",
    phone: "+60 12-397 8868",
    memberSince: "January 2025",
    avatar: require("../public/Asthon_Hall_69.jpg"),
  })

  const handleLogout = () => {
    logout()
  }

  const navigateToAccountDetails = () => {
    navigation.navigate("AccountDetails")
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Profile</Text>
        <TouchableOpacity style={styles.settingsButton}>
          <Feather name="settings" size={24} color={Colors.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* User Profile Card */}
        <AppCard style={styles.profileCard}>
          <View style={styles.profileHeader}>
            <Image source={userProfile.avatar} style={styles.avatar} />
            <View style={styles.profileInfo}>
              <Text style={styles.userName}>{userProfile.name}</Text>
              <Text style={styles.userEmail}>{userProfile.email}</Text>
              <Text style={styles.memberSince}>Member since {userProfile.memberSince}</Text>
            </View>
            <TouchableOpacity style={styles.editButton}>
              <Feather name="edit-2" size={16} color={Colors.primary} />
            </TouchableOpacity>
          </View>

          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>RM 2,450</Text>
              <Text style={styles.statLabel}>Total Spent</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>47</Text>
              <Text style={styles.statLabel}>Transactions</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>12</Text>
              <Text style={styles.statLabel}>Merchants</Text>
            </View>
          </View>
        </AppCard>

        {/* Account Management */}
        <AppCard style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Account Management</Text>

          <ProfileOption
            icon="credit-card"
            title="Account Details"
            subtitle="Manage cards, DuitNow & ZKP security"
            onPress={navigateToAccountDetails}
            showBadge={true}
          />

          <ProfileOption
            icon="shield"
            title="Security Settings"
            subtitle="Two-factor auth, biometrics"
            onPress={() => {}}
          />

          <ProfileOption icon="bell" title="Notifications" subtitle="Payment alerts, promotions" onPress={() => navigation.navigate("Notifications")} />

          <ProfileOption icon="globe" title="Language & Region" subtitle="English (Malaysia)" onPress={() => {}} />
        </AppCard>

        {/* Payment & Wallet */}
        <AppCard style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Payment & Wallet</Text>

          <ProfileOption
            icon="dollar-sign"
            title="Transaction History"
            subtitle="View all your payments"
            onPress={() => navigation.navigate("TransactionHistory")}
          />

          <ProfileOption
            icon="trending-up"
            title="Spending Analytics"
            subtitle="Track your expenses"
            onPress={() => {}}
          />

          <ProfileOption
            icon="gift"
            title="Rewards & Cashback"
            subtitle="Earn points on every transaction"
            onPress={() => {}}
          />

          <ProfileOption icon="users" title="Split Bills" subtitle="Share expenses with friends" onPress={() => {}} />
        </AppCard>

        {/* Support & Legal */}
        <AppCard style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Support & Legal</Text>

          <ProfileOption icon="help-circle" title="Help Center" subtitle="FAQs and support" onPress={() => {}} />

          <ProfileOption
            icon="message-circle"
            title="Contact Support"
            subtitle="Get help from our team"
            onPress={() => {}}
          />

          <ProfileOption icon="file-text" title="Terms & Privacy" subtitle="Legal information" onPress={() => {}} />

          <ProfileOption icon="star" title="Rate Open Payment" subtitle="Share your feedback" onPress={() => {}} />
        </AppCard>

        {/* Logout */}
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Feather name="log-out" size={20} color={Colors.danger} />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>

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
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: Colors.text,
  },
  settingsButton: {
    padding: 4,
  },
  scrollContainer: {
    flex: 1,
    padding: 20,
  },
  profileCard: {
    marginBottom: 20,
    padding: 20,
  },
  profileHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.border,
  },
  profileInfo: {
    flex: 1,
    marginLeft: 16,
  },
  userName: {
    fontSize: 20,
    fontWeight: "bold",
    color: Colors.text,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 2,
  },
  memberSince: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  editButton: {
    padding: 8,
  },
  statsContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: Colors.text,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: Colors.border,
  },
  sectionCard: {
    marginBottom: 20,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: Colors.text,
    marginBottom: 16,
  },
  profileOption: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderLight,
  },
  optionLeft: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  optionText: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 2,
  },
  optionSubtitle: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  optionRight: {
    flexDirection: "row",
    alignItems: "center",
  },
  notificationBadge: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: Colors.danger,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 8,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "bold",
    color: Colors.white,
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.dangerLight,
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.danger,
    marginLeft: 8,
  },
  bottomSpacing: {
    height: 40,
  },
})
