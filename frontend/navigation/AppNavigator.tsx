"use client"
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs"
import { createStackNavigator } from "@react-navigation/stack"
import { NavigationContainer } from "@react-navigation/native"
import { Feather } from "@expo/vector-icons"
import { useTheme } from "@shopify/restyle"
import { useAuth } from "../context/AuthContext"

// Auth Screens
import WelcomeScreen from "../screens/WelcomeScreen"
import UserLoginScreen from "../screens/UserLoginScreen"
import MerchantLoginScreen from "../screens/MerchantLoginScreen"

// eKYC Registration Screens
import RegisterStartScreen from "../screens/RegisterStartScreen"
import ScanICScreen from "../screens/ScanICScreen"
import FacialVerificationScreen from "../screens/FacialVerificationScreen"
import ConfirmDetailsScreen from "../screens/ConfirmDetailsScreen"
import AIVerificationScreen from "../screens/AIVerificationScreen"
import VerificationSuccessScreen from "../screens/VerificationSuccessScreen"
import VerificationFailedScreen from "../screens/VerificationFailedScreen"

// User App Screens
import HomeScreen from "../screens/HomeScreen"
import ScanScreen from "../screens/ScanScreen"
import WalletScreen from "../screens/WalletScreen"
import ProfileScreen from "../screens/ProfileScreen"
import AccountDetailsScreen from "../screens/AccountDetailsScreen"

// Merchant App Screens
import MerchantDashboardScreen from "../screens/merchant/MerchantDashboardScreen"
import MerchantScanFaceScreen from "../screens/merchant/MerchantScanFaceScreen"
import MerchantEnterAmountScreen from "../screens/merchant/MerchantEnterAmountScreen"
import MerchantReceiptScreen from "../screens/merchant/MerchantReceiptScreen"
import MerchantSettingsScreen from "../screens/merchant/MerchantSettingsScreen"

// Additional User Screens
import TransactionHistoryScreen from "../screens/TransactionHistoryScreen"
import TreeInvestmentScreen from "../screens/TreeInvestmentScreen"
import TreeLeaderboardScreen from "../screens/TreeLeaderboardScreen"
import AddMoneyScreen from "../screens/AddMoneyScreen"
import DepositSuccessScreen from "../screens/DepositSuccessScreen"
import BadgeRewardScreen from "../screens/BadgeRewardScreen"
import PaymentSuccessScreen from "../screens/PaymentSuccessScreen"
import PaymentProcessingScreen from "../screens/PaymentProcessingScreen"

// Notification and Security Screens
import NotificationsScreen from "../screens/NotificationsScreen"
import ZKPBlockedScreen from "../screens/ZKPBlockedScreen"
import UEBAVerificationScreen from "../screens/UEBAVerificationScreen"

// Type definitions for navigation stacks
type WalletStackParamList = {
  WalletHome: undefined
  TransactionHistory: undefined
  TreeInvestment: {
    updatedData?: {
      totalDeposit: number
      totalInterestEarned: number
      totalDonatedToReforestation: number
      daysActive: number
      progress: number
      badges: Array<{
        id: string
        name: string
        emoji: string
        description: string
        rarity: "common" | "rare" | "epic" | "legendary"
        unlockedAt: Date
      }>
    }
  }
  TreeLeaderboard: undefined
  AddMoney: undefined
  DepositSuccess: {
    depositData: {
      amount: number
      donationPercentage: number
      annualInterest: number
      donationAmount: number
      yourEarnings: number
    }
    progressGained: number
  }
  BadgeReward: {
    badge: {
      id: string
      name: string
      emoji: string
      description: string
      rarity: "common" | "rare" | "epic" | "legendary"
      unlockedAt: Date
    }
    treesPlanted: number
    co2Offset: number
    updatedInvestmentData: {
      totalDeposit: number
      totalInterestEarned: number
      totalDonatedToReforestation: number
      daysActive: number
      progress: number
      badges: Array<{
        id: string
        name: string
        emoji: string
        description: string
        rarity: "common" | "rare" | "epic" | "legendary"
        unlockedAt: Date
      }>
    }
  }
}

const Tab = createBottomTabNavigator()

// Define individual stack navigators for each tab and main flows
const AuthStack = createStackNavigator()
const ScanStack = createStackNavigator()
const WalletStack = createStackNavigator<WalletStackParamList>()
const ProfileInnerStack = createStackNavigator() // Renamed from Stack
const MerchantStack = createStackNavigator()
const HomeInnerStack = createStackNavigator() // Renamed from Stack
const RootStack = createStackNavigator() // Main stack for the entire app

const AuthStackNavigatorComponent = () => (
  <AuthStack.Navigator screenOptions={{ headerShown: false }}>
    <AuthStack.Screen name="Welcome" component={WelcomeScreen} />
    <AuthStack.Screen name="UserLogin" component={UserLoginScreen} />
    <AuthStack.Screen name="MerchantLogin" component={MerchantLoginScreen} />
    {/* eKYC Registration Flow */}
    <AuthStack.Screen name="RegisterStart" component={RegisterStartScreen} />
    <AuthStack.Screen name="ScanIC" component={ScanICScreen} />
    <AuthStack.Screen name="FacialVerification" component={FacialVerificationScreen} />
    <AuthStack.Screen name="ConfirmDetails" component={ConfirmDetailsScreen} />
    <AuthStack.Screen name="AIVerification" component={AIVerificationScreen} />
    <AuthStack.Screen name="VerificationSuccess" component={VerificationSuccessScreen} />
    <AuthStack.Screen name="VerificationFailed" component={VerificationFailedScreen} />
  </AuthStack.Navigator>
)

const ScanStackNavigatorComponent = () => (
  <ScanStack.Navigator screenOptions={{ headerShown: false }}>
    <ScanStack.Screen name="ScanHome" component={ScanScreen} />
    <ScanStack.Screen name="PaymentProcessing" component={PaymentProcessingScreen} />
    <ScanStack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} />
  </ScanStack.Navigator>
)

const WalletStackNavigatorComponent = () => (
  <WalletStack.Navigator screenOptions={{ headerShown: false }}>
    <WalletStack.Screen name="WalletHome" component={WalletScreen} />
    <WalletStack.Screen name="TransactionHistory" component={TransactionHistoryScreen} />
    <WalletStack.Screen name="TreeInvestment" component={TreeInvestmentScreen} />
    <WalletStack.Screen name="TreeLeaderboard" component={TreeLeaderboardScreen} />
    <WalletStack.Screen name="AddMoney" component={AddMoneyScreen} />
    <WalletStack.Screen name="DepositSuccess" component={DepositSuccessScreen} />
    <WalletStack.Screen name="BadgeReward" component={BadgeRewardScreen} />
  </WalletStack.Navigator>
)

const ProfileStackNavigatorComponent = () => (
  <ProfileInnerStack.Navigator screenOptions={{ headerShown: false }}>
    <ProfileInnerStack.Screen name="ProfileHome" component={ProfileScreen} />
    <ProfileInnerStack.Screen name="AccountDetails" component={AccountDetailsScreen} />
    <ProfileInnerStack.Screen name="Notifications" component={NotificationsScreen} />
    <ProfileInnerStack.Screen name="TransactionHistory" component={TransactionHistoryScreen} />
    <ProfileInnerStack.Screen name="ZKPBlocked" component={ZKPBlockedScreen} />
    <ProfileInnerStack.Screen name="UEBAVerification" component={UEBAVerificationScreen} />
    <ProfileInnerStack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} />
  </ProfileInnerStack.Navigator>
)

const MerchantStackNavigatorComponent = () => (
  <MerchantStack.Navigator screenOptions={{ headerShown: false }}>
    <MerchantStack.Screen name="MerchantDashboard" component={MerchantDashboardScreen} />
    <MerchantStack.Screen name="MerchantScanFace" component={MerchantScanFaceScreen} />
    <MerchantStack.Screen name="MerchantEnterAmount" component={MerchantEnterAmountScreen} />
    <MerchantStack.Screen name="MerchantReceipt" component={MerchantReceiptScreen} />
    <MerchantStack.Screen name="MerchantSettings" component={MerchantSettingsScreen} />
  </MerchantStack.Navigator>
)

const HomeStackNavigatorComponent = () => (
  <HomeInnerStack.Navigator screenOptions={{ headerShown: false }}>
    <HomeInnerStack.Screen name="Home" component={HomeScreen} />
    <HomeInnerStack.Screen name="Notifications" component={NotificationsScreen} />
    <HomeInnerStack.Screen name="ZKPBlocked" component={ZKPBlockedScreen} />
    <HomeInnerStack.Screen name="UEBAVerification" component={UEBAVerificationScreen} />
    <HomeInnerStack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} />
    <HomeInnerStack.Screen name="AccountDetails" component={AccountDetailsScreen} />
    <HomeInnerStack.Screen name="TransactionHistory" component={TransactionHistoryScreen} />
  </HomeInnerStack.Navigator>
)

const UserTabs = () => {
  const theme = useTheme()
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, any> = {
            Home: "home",
            Scan: "maximize",
            Wallet: "credit-card",
            Profile: "user",
          }
          return <Feather name={icons[route.name]} size={24} color={color} />
        },
        tabBarActiveTintColor: theme.colors.primaryAction,
        tabBarInactiveTintColor: theme.colors.secondaryText,
        tabBarStyle: {
          backgroundColor: theme.colors.cardPrimaryBackground,
          borderTopWidth: 0,
          height: 90,
          paddingTop: 10,
          paddingBottom: 30,
          borderTopLeftRadius: 20,
          borderTopRightRadius: 20,
        },
        tabBarLabelStyle: { fontWeight: "600", fontSize: 12 },
      })}
    >
      <Tab.Screen name="Home" component={HomeStackNavigatorComponent} />
      <Tab.Screen name="Scan" component={ScanStackNavigatorComponent} />
      <Tab.Screen name="Wallet" component={WalletStackNavigatorComponent} />
      <Tab.Screen name="Profile" component={ProfileStackNavigatorComponent} />
    </Tab.Navigator>
  )
}

const MerchantTabs = () => {
  const theme = useTheme()
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, any> = {
            Dashboard: "home",
            Transactions: "credit-card",
            Analytics: "bar-chart-2",
            Profile: "user",
            Settings: "settings",
          }
          return <Feather name={icons[route.name]} size={24} color={color} />
        },
        tabBarActiveTintColor: theme.colors.primaryAction,
        tabBarInactiveTintColor: theme.colors.secondaryText,
        tabBarStyle: {
          backgroundColor: theme.colors.cardPrimaryBackground,
          borderTopWidth: 0,
          height: 90,
          paddingTop: 10,
          paddingBottom: 30,
          borderTopLeftRadius: 20,
          borderTopRightRadius: 20,
        },
        tabBarLabelStyle: { fontWeight: "600", fontSize: 12 },
      })}
    >
      <Tab.Screen name="Dashboard" component={MerchantStackNavigatorComponent} />
      <Tab.Screen name="Transactions" component={MerchantStackNavigatorComponent} />
      <Tab.Screen name="Analytics" component={MerchantStackNavigatorComponent} />
      <Tab.Screen name="Profile" component={ProfileStackNavigatorComponent} />
      <Tab.Screen name="Settings" component={MerchantSettingsScreen} />
    </Tab.Navigator>
  )
}

export default function AppNavigator() {
  const { isAuthenticated, userType } = useAuth()
  const theme = useTheme() // Get theme here

  return (
    <NavigationContainer>
      <RootStack.Navigator
        screenOptions={{
          headerShown: false,
          // Apply the main background color to the entire stack container
          contentStyle: { backgroundColor: theme.colors.mainBackground },
        }}
      >
        {!isAuthenticated ? (
          <RootStack.Screen name="Auth" component={AuthStackNavigatorComponent} />
        ) : userType === "merchant" ? (
          <RootStack.Screen name="MerchantApp" component={MerchantTabs} />
        ) : (
          <RootStack.Screen name="UserApp" component={UserTabs} />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  )
}
