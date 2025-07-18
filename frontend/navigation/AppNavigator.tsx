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

// User App Screens
import HomeScreen from "../screens/HomeScreen";
import ScanScreen from "../screens/ScanScreen";
import WalletScreen from "../screens/WalletScreen";
import ProfileScreen from "../screens/ProfileScreen";

// Merchant App Screens
import MerchantDashboardScreen from "../screens/merchant/MerchantDashboardScreen";
import MerchantScanFaceScreen from "../screens/merchant/MerchantScanFaceScreen";
import MerchantEnterAmountScreen from "../screens/merchant/MerchantEnterAmountScreen";
import MerchantReceiptScreen from "../screens/merchant/MerchantReceiptScreen";
import MerchantSettingsScreen from "../screens/merchant/MerchantSettingsScreen";

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

const AuthStack = () => (
  <AuthStackNavigator.Navigator screenOptions={{ headerShown: false }}>
    <AuthStackNavigator.Screen name="Welcome" component={WelcomeScreen} />
    <AuthStackNavigator.Screen name="UserLogin" component={UserLoginScreen} />
    <AuthStackNavigator.Screen
      name="MerchantLogin"
      component={MerchantLoginScreen}
    />
  </AuthStackNavigator.Navigator>
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
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Scan" component={ScanStack} />
      <Tab.Screen name="Wallet" component={WalletStack} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
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
      <Tab.Screen name="Dashboard" component={MerchantStack} />
      <Tab.Screen name="Transactions" component={MerchantStack} />
      <Tab.Screen name="Analytics" component={MerchantStack} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
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
