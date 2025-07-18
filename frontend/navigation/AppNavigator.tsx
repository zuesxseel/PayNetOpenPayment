"use client";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";
import { NavigationContainer } from "@react-navigation/native";
import { Feather } from "@expo/vector-icons";
import { useTheme } from "@shopify/restyle";
import { useAuth } from "../context/AuthContext";

// Auth Screens
import WelcomeScreen from "../screens/WelcomeScreen";
import UserLoginScreen from "../screens/UserLoginScreen";
import MerchantLoginScreen from "../screens/MerchantLoginScreen";

// eKYC Registration Screens
import RegisterStartScreen from "../screens/RegisterStartScreen";
import ScanICScreen from "../screens/ScanICScreen";
import FacialVerificationScreen from "../screens/FacialVerificationScreen";
import ConfirmDetailsScreen from "../screens/ConfirmDetailsScreen";
import AIVerificationScreen from "../screens/AIVerificationScreen";
import VerificationSuccessScreen from "../screens/VerificationSuccessScreen";
import VerificationFailedScreen from "../screens/VerificationFailedScreen";

// User App Screens
import HomeScreen from "../screens/HomeScreen";
import ScanScreen from "../screens/ScanScreen";
import WalletScreen from "../screens/WalletScreen";
import ProfileScreen from "../screens/ProfileScreen";
import AccountDetailsScreen from "@/screens/AccountDetailsScreen";
// Merchant App Screens
import MerchantDashboardScreen from "../screens/merchant/MerchantDashboardScreen";
import MerchantScanFaceScreen from "../screens/merchant/MerchantScanFaceScreen";
import MerchantEnterAmountScreen from "../screens/merchant/MerchantEnterAmountScreen";
import MerchantReceiptScreen from "../screens/merchant/MerchantReceiptScreen";
import MerchantSettingsScreen from "../screens/merchant/MerchantSettingsScreen"; // Declared the variable here

// Additional User Screens
import TransactionHistoryScreen from "../screens/TransactionHistoryScreen";
import TreeInvestmentScreen from "../screens/TreeInvestmentScreen";
import TreeLeaderboardScreen from "../screens/TreeLeaderboardScreen";
import AddMoneyScreen from "../screens/AddMoneyScreen";
import DepositSuccessScreen from "../screens/DepositSuccessScreen";
import BadgeRewardScreen from "../screens/BadgeRewardScreen";
import PaymentSuccessScreen from "../screens/PaymentSuccessScreen";
import PaymentProcessingScreen from "../screens/PaymentProcessingScreen";

// Type definitions for navigation stacks
type WalletStackParamList = {
  WalletHome: undefined;
  TransactionHistory: undefined;
  TreeInvestment: {
    updatedData?: {
      totalDeposit: number;
      totalInterestEarned: number;
      totalDonatedToReforestation: number;
      daysActive: number;
      progress: number;
      badges: Array<{
        id: string;
        name: string;
        emoji: string;
        description: string;
        rarity: "common" | "rare" | "epic" | "legendary";
        unlockedAt: Date;
      }>;
    };
  };
  TreeLeaderboard: undefined;
  AddMoney: undefined;
  DepositSuccess: {
    depositData: {
      amount: number;
      donationPercentage: number;
      annualInterest: number;
      donationAmount: number;
      yourEarnings: number;
    };
    progressGained: number;
  };
  BadgeReward: {
    badge: {
      id: string;
      name: string;
      emoji: string;
      description: string;
      rarity: "common" | "rare" | "epic" | "legendary";
      unlockedAt: Date;
    };
    treesPlanted: number;
    co2Offset: number;
    updatedInvestmentData: {
      totalDeposit: number;
      totalInterestEarned: number;
      totalDonatedToReforestation: number;
      daysActive: number;
      progress: number;
      badges: Array<{
        id: string;
        name: string;
        emoji: string;
        description: string;
        rarity: "common" | "rare" | "epic" | "legendary";
        unlockedAt: Date;
      }>;
    };
  };
};

const Tab = createBottomTabNavigator();
const AuthStackNavigator = createStackNavigator();
const ScanStackNavigator = createStackNavigator();
const WalletStackNavigator = createStackNavigator<WalletStackParamList>();
const MerchantStackNavigator = createStackNavigator();

// Notification and Security Screens
import NotificationsScreen from "../screens/NotificationsScreen";
import ZKPBlockedScreen from "../screens/ZKPBlockedScreen";
import UEBAVerificationScreen from "../screens/UEBAVerificationScreen";

const Stack = createStackNavigator();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Welcome" component={WelcomeScreen} />
    <Stack.Screen name="UserLogin" component={UserLoginScreen} />
    <Stack.Screen name="MerchantLogin" component={MerchantLoginScreen} />

    {/* eKYC Registration Flow */}
    <Stack.Screen name="RegisterStart" component={RegisterStartScreen} />
    <Stack.Screen name="ScanIC" component={ScanICScreen} />
    <Stack.Screen
      name="FacialVerification"
      component={FacialVerificationScreen}
    />
    <Stack.Screen name="ConfirmDetails" component={ConfirmDetailsScreen} />
    <Stack.Screen name="AIVerification" component={AIVerificationScreen} />
    <Stack.Screen
      name="VerificationSuccess"
      component={VerificationSuccessScreen}
    />
    <Stack.Screen
      name="VerificationFailed"
      component={VerificationFailedScreen}
    />
  </Stack.Navigator>
);

const ScanStack = () => (
  <ScanStackNavigator.Navigator screenOptions={{ headerShown: false }}>
    <ScanStackNavigator.Screen name="ScanHome" component={ScanScreen} />
    <ScanStackNavigator.Screen
      name="PaymentProcessing"
      component={PaymentProcessingScreen}
    />
    <ScanStackNavigator.Screen
      name="PaymentSuccess"
      component={PaymentSuccessScreen}
    />
  </ScanStackNavigator.Navigator>
);

const WalletStack = () => (
  <WalletStackNavigator.Navigator screenOptions={{ headerShown: false }}>
    <WalletStackNavigator.Screen name="WalletHome" component={WalletScreen} />
    <WalletStackNavigator.Screen
      name="TransactionHistory"
      component={TransactionHistoryScreen}
    />
    <WalletStackNavigator.Screen
      name="TreeInvestment"
      component={TreeInvestmentScreen}
    />
    <WalletStackNavigator.Screen
      name="TreeLeaderboard"
      component={TreeLeaderboardScreen}
    />
    <WalletStackNavigator.Screen name="AddMoney" component={AddMoneyScreen} />
    <WalletStackNavigator.Screen
      name="DepositSuccess"
      component={DepositSuccessScreen}
    />
    <WalletStackNavigator.Screen
      name="BadgeReward"
      component={BadgeRewardScreen}
    />
  </WalletStackNavigator.Navigator>
);

const ProfileStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ProfileHome" component={ProfileScreen} />
    <Stack.Screen name="AccountDetails" component={AccountDetailsScreen} />
    <Stack.Screen name="Notifications" component={NotificationsScreen} />
    <Stack.Screen
      name="TransactionHistory"
      component={TransactionHistoryScreen}
    />
    <Stack.Screen name="ZKPBlocked" component={ZKPBlockedScreen} />
    <Stack.Screen name="UEBAVerification" component={UEBAVerificationScreen} />
    <Stack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} />
  </Stack.Navigator>
);

const MerchantStack = () => (
  <MerchantStackNavigator.Navigator screenOptions={{ headerShown: false }}>
    <MerchantStackNavigator.Screen
      name="MerchantDashboard"
      component={MerchantDashboardScreen}
    />
    <MerchantStackNavigator.Screen
      name="MerchantScanFace"
      component={MerchantScanFaceScreen}
    />
    <MerchantStackNavigator.Screen
      name="MerchantEnterAmount"
      component={MerchantEnterAmountScreen}
    />
    <MerchantStackNavigator.Screen
      name="MerchantReceipt"
      component={MerchantReceiptScreen}
    />
    <MerchantStackNavigator.Screen
      name="MerchantSettings"
      component={MerchantSettingsScreen}
    />
  </MerchantStackNavigator.Navigator>
);

const HomeStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Home" component={HomeScreen} />
    <Stack.Screen name="Notifications" component={NotificationsScreen} />
    <Stack.Screen name="ZKPBlocked" component={ZKPBlockedScreen} />
    <Stack.Screen name="UEBAVerification" component={UEBAVerificationScreen} />
    <Stack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} />
  </Stack.Navigator>
);

const UserTabs = () => {
  const theme = useTheme();
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
          };
          return <Feather name={icons[route.name]} size={24} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primaryAction,
        tabBarInactiveTintColor: theme.colors.secondaryText,
        tabBarStyle: {
          backgroundColor: theme.colors.cardPrimaryBackground,
          borderTopWidth: 0,
          height: 90,
          paddingTop: 10,
          paddingBottom: 30,
        },
        tabBarLabelStyle: { fontWeight: "600", fontSize: 12 },
      })}
    >
      <Tab.Screen name="Home" component={HomeStack} />
      <Tab.Screen name="Scan" component={ScanStack} />
      <Tab.Screen name="Wallet" component={WalletStack} />
      <Tab.Screen name="Profile" component={ProfileStack} />
    </Tab.Navigator>
  );
};

const MerchantTabs = () => {
  const theme = useTheme();
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
          };
          return <Feather name={icons[route.name]} size={24} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primaryAction,
        tabBarInactiveTintColor: theme.colors.secondaryText,
        tabBarStyle: {
          backgroundColor: theme.colors.cardPrimaryBackground,
          borderTopWidth: 0,
          height: 90,
          paddingTop: 10,
          paddingBottom: 30,
        },
        tabBarLabelStyle: { fontWeight: "600", fontSize: 12 },
      })}
    >
      {" "}
      <Tab.Screen name="Dashboard" component={MerchantStack} />
      <Tab.Screen name="Transactions" component={MerchantStack} />
      <Tab.Screen name="Analytics" component={MerchantStack} />
      <Tab.Screen name="Profile" component={ProfileStack} />
      <Tab.Screen name="Settings" component={MerchantSettingsScreen} />
    </Tab.Navigator>
  );
};

export default function AppNavigator() {
  const { isAuthenticated, userType } = useAuth();

  if (!isAuthenticated) {
    return (
      <NavigationContainer>
        <AuthStack />
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer>
      {userType === "merchant" ? <MerchantTabs /> : <UserTabs />}
    </NavigationContainer>
  );
}
