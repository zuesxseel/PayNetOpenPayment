"use client";
import { useState, useRef, useCallback } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  ScrollView,
  TouchableOpacity,
  TextInput,
  View,
  PanResponder,
  Animated,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import { Box, Text, Button } from "../components/Themed";
import { useTheme } from "@shopify/restyle";
import { MotiView } from "moti";
import type { StackNavigationProp } from "@react-navigation/stack";
import type { RouteProp } from "@react-navigation/native";

// Type definitions
type RootStackParamList = {
  TreeInvestment: undefined;
  AddMoney: undefined;
  DepositSuccess: {
    depositData: DepositData;
    progressGained: number;
  };
  BadgeReward: {
    badge: Badge;
    treesPlanted: number;
    co2Offset: number;
  };
};

type AddMoneyScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "AddMoney"
>;

type AddMoneyScreenRouteProp = RouteProp<RootStackParamList, "AddMoney">;

interface AddMoneyScreenProps {
  navigation: AddMoneyScreenNavigationProp;
  route: AddMoneyScreenRouteProp;
}

interface DepositData {
  amount: number;
  donationPercentage: number;
  annualInterest: number;
  donationAmount: number;
  yourEarnings: number;
}

interface Badge {
  id: string;
  name: string;
  emoji: string;
  description: string;
  rarity: "common" | "rare" | "epic" | "legendary";
  unlockedAt: Date;
}

// High-Performance Custom Slider Component
interface CustomSliderProps {
  value: number[];
  onValueChange: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
}

const CustomSlider = ({
  value,
  onValueChange,
  min = 0,
  max = 100,
  step = 5,
}: CustomSliderProps) => {
  const theme = useTheme();
  const currentValue = Array.isArray(value) ? value[0] : value;
  const percentage = ((currentValue - min) / (max - min)) * 100;

  // Animation and layout refs
  const pan = useRef(new Animated.Value(0)).current;
  const sliderWidth = useRef(0);
  const isDragging = useRef(false);
  const lastUpdateTime = useRef(0);

  // Memoized value calculation for performance
  const calculateValue = useCallback(
    (gestureX: number, width: number) => {
      const newPercentage = Math.max(
        0,
        Math.min(100, (gestureX / width) * 100)
      );
      const rawValue = (newPercentage / 100) * (max - min) + min;
      const steppedValue = Math.round(rawValue / step) * step;
      return Math.max(min, Math.min(max, steppedValue));
    },
    [min, max, step]
  );

  // Throttled update function to prevent excessive re-renders (~60fps)
  const throttledUpdate = useCallback(
    (newValue: number) => {
      const now = Date.now();
      if (now - lastUpdateTime.current > 16) {
        // ~60fps throttling
        lastUpdateTime.current = now;
        onValueChange([newValue]);
      }
    },
    [onValueChange]
  );

  // Pan responder for smooth drag gestures
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onStartShouldSetPanResponderCapture: () => true,
      onMoveShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponderCapture: () => true,

      onPanResponderGrant: (evt) => {
        isDragging.current = true;
        const { locationX } = evt.nativeEvent;
        const newValue = calculateValue(locationX, sliderWidth.current);
        onValueChange([newValue]);
      },

      onPanResponderMove: (evt, gestureState) => {
        if (!isDragging.current) return;

        const { locationX } = evt.nativeEvent;
        const clampedX = Math.max(0, Math.min(sliderWidth.current, locationX));
        const newValue = calculateValue(clampedX, sliderWidth.current);

        // Update value with throttling for smooth performance
        throttledUpdate(newValue);
      },

      onPanResponderTerminationRequest: () => false,

      onPanResponderRelease: () => {
        isDragging.current = false;
      },

      onPanResponderTerminate: () => {
        isDragging.current = false;
      },
    })
  ).current;

  // Handle layout measurement for dynamic width
  const onLayout = useCallback((event: any) => {
    sliderWidth.current = event.nativeEvent.layout.width;
  }, []);

  return (
    <View
      style={{
        height: 40, // Larger touch area for better UX
        width: "100%",
        justifyContent: "center",
        paddingVertical: 16, // Extra padding for easier touch
      }}
      onLayout={onLayout}
      {...panResponder.panHandlers}
    >
      {/* Track background */}
      <View
        style={{
          height: 8,
          width: "100%",
          backgroundColor: theme.colors.cardBorder,
          borderRadius: 4,
          position: "absolute",
        }}
      />

      {/* Active track */}
      <View
        style={{
          height: 8,
          width: `${percentage}%`,
          backgroundColor: theme.colors.success,
          borderRadius: 4,
          position: "absolute",
        }}
      />

      {/* Thumb with shadow and larger touch area */}
      <View
        style={{
          position: "absolute",
          left: `${percentage}%`,
          marginLeft: -12, // Center the thumb
          width: 24,
          height: 24,
          backgroundColor: theme.colors.success,
          borderRadius: 12,
          borderWidth: 3,
          borderColor: theme.colors.cardPrimaryBackground,
          shadowColor: "#000",
          shadowOffset: {
            width: 0,
            height: 2,
          },
          shadowOpacity: 0.25,
          shadowRadius: 3.84,
          elevation: 5,
        }}
      />
    </View>
  );
};

export default function AddMoneyScreen({ navigation }: AddMoneyScreenProps) {
  const theme = useTheme();
  const [amount, setAmount] = useState("");
  const [donationPercentage, setDonationPercentage] = useState([50]); // Default 50%

  const interestRate = 2.5; // 2.5% annual interest
  const calculatedAmount = Number.parseFloat(amount) || 0;
  const annualInterest = calculatedAmount * (interestRate / 100);
  const donationAmount = annualInterest * (donationPercentage[0] / 100);
  const yourEarnings = annualInterest - donationAmount;

  const handleConfirm = () => {
    if (calculatedAmount > 0) {
      const depositData: DepositData = {
        amount: calculatedAmount,
        donationPercentage: donationPercentage[0],
        annualInterest,
        donationAmount,
        yourEarnings,
      };

      // Calculate progress gained
      const progressGained = (calculatedAmount / 100) * 10; // 10% per RM 100

      // Navigate to success screen with data
      navigation.navigate("DepositSuccess", {
        depositData,
        progressGained,
      });
    }
  };

  const handleCancel = () => {
    navigation.goBack();
  };

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        {/* Header */}
        <Box
          flexDirection="row"
          alignItems="center"
          padding="l"
          backgroundColor="cardPrimaryBackground"
        >
          <TouchableOpacity onPress={handleCancel}>
            <Feather
              name="arrow-left"
              size={24}
              color={theme.colors.primaryText}
            />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Add to T+ Tree
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            {/* Amount Input */}
            <Box marginBottom="l">
              <Text
                variant="body"
                fontWeight="600"
                color="primaryText"
                marginBottom="s"
              >
                Deposit Amount
              </Text>
              <Box
                flexDirection="row"
                alignItems="center"
                backgroundColor="cardPrimaryBackground"
                borderRadius="m"
                paddingHorizontal="m"
                borderWidth={1}
                borderColor="cardBorder"
              >
                <Text
                  variant="body"
                  fontSize={18}
                  fontWeight="600"
                  color="primaryText"
                >
                  RM
                </Text>
                <TextInput
                  value={amount}
                  onChangeText={setAmount}
                  placeholder="0.00"
                  keyboardType="decimal-pad"
                  style={{
                    flex: 1,
                    height: 50,
                    marginLeft: theme.spacing.s,
                    fontSize: 18,
                    fontWeight: "600",
                    color: theme.colors.primaryText,
                  }}
                />
              </Box>
            </Box>

            {/* Interest Rate Info */}
            <Box
              backgroundColor="blueLight"
              padding="m"
              borderRadius="m"
              marginBottom="l"
            >
              <Box flexDirection="row" alignItems="center" marginBottom="s">
                <Feather
                  name="trending-up"
                  size={16}
                  color={theme.colors.primaryAction}
                />
                <Text
                  variant="body"
                  fontSize={14}
                  fontWeight="600"
                  color="primaryAction"
                  marginLeft="xs"
                >
                  Deposit Terms
                </Text>
              </Box>
              <Text variant="body" fontSize={13} color="secondaryText">
                • Annual Interest Rate: {interestRate}%
              </Text>
            </Box>

            {/* Donation Percentage Slider */}
            <Box marginBottom="l">
              <Box
                flexDirection="row"
                justifyContent="space-between"
                alignItems="center"
                marginBottom="m"
              >
                <Text variant="body" fontWeight="600" color="primaryText">
                  Donation Split
                </Text>
                <Box
                  backgroundColor="success"
                  paddingHorizontal="s"
                  paddingVertical="xs"
                  borderRadius="s"
                >
                  <Text
                    variant="body"
                    fontSize={12}
                    color="primaryActionText"
                    fontWeight="600"
                  >
                    {donationPercentage[0]}% to Trees
                  </Text>
                </Box>
              </Box>

              <Box marginBottom="m">
                <CustomSlider
                  value={donationPercentage}
                  onValueChange={setDonationPercentage}
                  max={100}
                  min={0}
                  step={5}
                />
              </Box>

              <Box flexDirection="row" justifyContent="space-between">
                <Text variant="body" fontSize={12} color="secondaryText">
                  0% (Keep all interest)
                </Text>
                <Text variant="body" fontSize={12} color="secondaryText">
                  100% (Donate all interest)
                </Text>
              </Box>
            </Box>

            {/* Calculation Breakdown */}
            {calculatedAmount > 0 && (
              <Box
                backgroundColor="cardPrimaryBackground"
                padding="m"
                borderRadius="m"
                marginBottom="l"
              >
                <Text
                  variant="body"
                  fontWeight="600"
                  color="primaryText"
                  marginBottom="s"
                >
                  Annual Breakdown
                </Text>

                <Box
                  flexDirection="row"
                  justifyContent="space-between"
                  marginBottom="xs"
                >
                  <Text variant="body" fontSize={14} color="secondaryText">
                    Total Interest Earned
                  </Text>
                  <Text
                    variant="body"
                    fontSize={14}
                    fontWeight="600"
                    color="primaryText"
                  >
                    RM {annualInterest.toFixed(2)}
                  </Text>
                </Box>

                <Box
                  flexDirection="row"
                  justifyContent="space-between"
                  marginBottom="xs"
                >
                  <Text variant="body" fontSize={14} color="secondaryText">
                    Donated to Reforestation
                  </Text>
                  <Text
                    variant="body"
                    fontSize={14}
                    fontWeight="600"
                    color="success"
                  >
                    RM {donationAmount.toFixed(2)}
                  </Text>
                </Box>

                <Box
                  flexDirection="row"
                  justifyContent="space-between"
                  marginBottom="xs"
                >
                  <Text variant="body" fontSize={14} color="secondaryText">
                    Your Earnings
                  </Text>
                  <Text
                    variant="body"
                    fontSize={14}
                    fontWeight="600"
                    color="primaryAction"
                  >
                    RM {yourEarnings.toFixed(2)}
                  </Text>
                </Box>

                <Box
                  height={1}
                  backgroundColor="cardBorder"
                  marginVertical="s"
                />

                <Box backgroundColor="success" padding="s" borderRadius="s">
                  <Text
                    variant="body"
                    fontSize={12}
                    color="primaryActionText"
                    textAlign="center"
                  >
                    🌱 Your donation will plant approximately{" "}
                    {Math.floor(donationAmount / 5)} trees
                  </Text>
                </Box>
              </Box>
            )}

            {/* Action Buttons */}
            <Box flexDirection="row" gap="m" marginBottom="l">
              <Box flex={1}>
                <Button
                  label="Cancel"
                  onPress={handleCancel}
                  variant="outline"
                />
              </Box>
              <Box flex={1}>
                <Button
                  label="Confirm Deposit"
                  onPress={handleConfirm}
                  disabled={calculatedAmount <= 0}
                />
              </Box>
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  );
}
