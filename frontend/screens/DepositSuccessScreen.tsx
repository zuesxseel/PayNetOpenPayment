"use client";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, TouchableOpacity } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Box, Text, Button } from "../components/Themed";
import { useTheme } from "@shopify/restyle";
import { MotiView } from "moti";
import type { StackNavigationProp } from "@react-navigation/stack";
import type { RouteProp } from "@react-navigation/native";

// Type definitions
type RootStackParamList = {
  WalletHome: undefined;
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
  DepositSuccess: {
    depositData: DepositData;
    progressGained: number;
  };
  TreeLeaderboard: undefined;
  BadgeReward: {
    badge: Badge;
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

type DepositSuccessScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "DepositSuccess"
>;

type DepositSuccessScreenRouteProp = RouteProp<
  RootStackParamList,
  "DepositSuccess"
>;

interface DepositSuccessScreenProps {
  navigation: DepositSuccessScreenNavigationProp;
  route: DepositSuccessScreenRouteProp;
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

export default function DepositSuccessScreen({
  navigation,
  route,
}: DepositSuccessScreenProps) {
  const theme = useTheme();
  const { depositData, progressGained } = route.params;

  const treesPlanted = Math.floor(depositData.donationAmount / 5);
  const co2Absorbed = treesPlanted * 25; // Approximate kg CO2 per tree per year

  // Simulate current investment data (in a real app, this would come from a database/API)
  const currentInvestmentData = {
    totalDeposit: 2000.0, // This should be fetched from storage/API
    totalInterestEarned: 50.32,
    totalDonatedToReforestation: 25.16,
    daysActive: 45,
    progress: 32, // This should be fetched from storage/API
    badges: [] as Array<{
      id: string;
      name: string;
      emoji: string;
      description: string;
      rarity: "common" | "rare" | "epic" | "legendary";
      unlockedAt: Date;
    }>,
  };

  // Calculate updated investment data
  const updatedInvestmentData = {
    ...currentInvestmentData,
    totalDeposit: currentInvestmentData.totalDeposit + depositData.amount,
    totalDonatedToReforestation:
      currentInvestmentData.totalDonatedToReforestation +
      depositData.donationAmount,
    progress: Math.min(100, currentInvestmentData.progress + progressGained), // Cap at 100%
  };

  // Badge system - check if tree is complete
  const getBadgeForProgress = (progress: number, totalDeposit: number) => {
    if (progress >= 100) {
      if (totalDeposit >= 10000) {
        return {
          id: "legendary_forest_guardian",
          name: "Legendary Forest Guardian",
          emoji: "🌲",
          description:
            "You've invested over RM 10,000 and grown a magnificent tree! Your dedication to reforestation is legendary.",
          rarity: "legendary" as const,
          unlockedAt: new Date(),
        };
      } else if (totalDeposit >= 5000) {
        return {
          id: "epic_tree_champion",
          name: "Epic Tree Champion",
          emoji: "🌳",
          description:
            "With over RM 5,000 invested, you've become a true champion of environmental conservation!",
          rarity: "epic" as const,
          unlockedAt: new Date(),
        };
      } else if (totalDeposit >= 2000) {
        return {
          id: "rare_eco_warrior",
          name: "Rare Eco Warrior",
          emoji: "🌿",
          description:
            "Your RM 2,000+ investment shows you're a dedicated warrior for our planet's future!",
          rarity: "rare" as const,
          unlockedAt: new Date(),
        };
      } else {
        return {
          id: "common_tree_grower",
          name: "Tree Grower",
          emoji: "🌱",
          description:
            "Congratulations on growing your first complete tree! Every journey starts with a single seed.",
          rarity: "common" as const,
          unlockedAt: new Date(),
        };
      }
    }
    return null;
  };

  const earnedBadge = getBadgeForProgress(
    updatedInvestmentData.progress,
    updatedInvestmentData.totalDeposit
  );

  // Add the new badge to the collection if earned
  if (earnedBadge) {
    updatedInvestmentData.badges = [
      ...currentInvestmentData.badges,
      earnedBadge,
    ];
  }

  const handleViewLeaderboard = () => {
    navigation.navigate("TreeLeaderboard");
  };

  const handleContinueGrowing = () => {
    if (earnedBadge) {
      // Navigate to badge reward screen first
      navigation.navigate("BadgeReward", {
        badge: earnedBadge,
        treesPlanted,
        co2Offset: co2Absorbed,
        updatedInvestmentData,
      });
    } else {
      // Reset navigation stack to remove deposit screens from history
      navigation.reset({
        index: 1,
        routes: [
          { name: "WalletHome" },
          {
            name: "TreeInvestment",
            params: { updatedData: updatedInvestmentData },
          },
        ],
      });
    }
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
          <TouchableOpacity onPress={handleContinueGrowing}>
            <Feather
              name="arrow-left"
              size={24}
              color={theme.colors.primaryText}
            />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Deposit Successful
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          {/* Success Header */}
          <MotiView
            from={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box alignItems="center" marginBottom="l">
              <MotiView
                from={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "timing", duration: 600, delay: 200 }}
              >
                <Box
                  width={80}
                  height={80}
                  backgroundColor="success"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                  marginBottom="m"
                >
                  <Feather
                    name="check"
                    size={40}
                    color={theme.colors.primaryActionText}
                  />
                </Box>
              </MotiView>

              <Text variant="title2" color="success" textAlign="center">
                🎉 Deposit Successful!
              </Text>
              <Text
                variant="body"
                color="secondaryText"
                textAlign="center"
                marginTop="s"
              >
                Your T+ Tree investment is growing
              </Text>
            </Box>
          </MotiView>

          {/* Progress Gained */}
          {progressGained > 0 && (
            <MotiView
              from={{ opacity: 0, translateY: 20 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ type: "timing", delay: 300 }}
            >
              <Box
                backgroundColor="blueLight"
                padding="m"
                borderRadius="m"
                marginBottom="l"
              >
                <Box
                  flexDirection="row"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text variant="body" fontSize={20}>
                    🌱
                  </Text>
                  <Text
                    variant="body"
                    fontWeight="600"
                    color="primaryAction"
                    marginLeft="s"
                  >
                    Tree Growth: +{progressGained.toFixed(1)}%
                  </Text>
                </Box>
                <Text
                  variant="body"
                  fontSize={12}
                  color="secondaryText"
                  textAlign="center"
                  marginTop="xs"
                >
                  Your tree is getting stronger! 🌿
                </Text>
              </Box>
            </MotiView>
          )}

          {/* Deposit Summary */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box
              backgroundColor="cardPrimaryBackground"
              padding="l"
              borderRadius="m"
              marginBottom="l"
            >
              <Text
                variant="body"
                fontWeight="600"
                color="primaryText"
                marginBottom="m"
                textAlign="center"
              >
                Deposit Summary
              </Text>

              <Box
                flexDirection="row"
                justifyContent="space-between"
                marginBottom="s"
              >
                <Text variant="body" fontSize={14} color="secondaryText">
                  Amount Deposited
                </Text>
                <Text
                  variant="body"
                  fontSize={14}
                  fontWeight="600"
                  color="primaryText"
                >
                  RM {depositData.amount.toFixed(2)}
                </Text>
              </Box>

              <Box
                flexDirection="row"
                justifyContent="space-between"
                marginBottom="s"
              >
                <Text variant="body" fontSize={14} color="secondaryText">
                  Annual Interest (2.5%)
                </Text>
                <Text
                  variant="body"
                  fontSize={14}
                  fontWeight="600"
                  color="success"
                >
                  RM {depositData.annualInterest.toFixed(2)}
                </Text>
              </Box>

              <Box
                flexDirection="row"
                justifyContent="space-between"
                marginBottom="s"
              >
                <Text variant="body" fontSize={14} color="secondaryText">
                  Your Earnings ({100 - depositData.donationPercentage}%)
                </Text>
                <Text
                  variant="body"
                  fontSize={14}
                  fontWeight="600"
                  color="primaryAction"
                >
                  RM {depositData.yourEarnings.toFixed(2)}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between">
                <Text variant="body" fontSize={14} color="secondaryText">
                  Donated to Trees ({depositData.donationPercentage}%)
                </Text>
                <Text
                  variant="body"
                  fontSize={14}
                  fontWeight="600"
                  color="treeGreen"
                >
                  RM {depositData.donationAmount.toFixed(2)}
                </Text>
              </Box>
            </Box>
          </MotiView>

          {/* Environmental Impact */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 500 }}
          >
            <Box
              backgroundColor="greenLight"
              padding="l"
              borderRadius="m"
              marginBottom="l"
            >
              <Box flexDirection="row" alignItems="center" marginBottom="m">
                <Text variant="body" fontSize={20}>
                  🌍
                </Text>
                <Text
                  variant="body"
                  fontWeight="600"
                  color="success"
                  marginLeft="s"
                >
                  Environmental Impact
                </Text>
              </Box>

              <Box
                flexDirection="row"
                justifyContent="space-between"
                marginBottom="s"
              >
                <Box alignItems="center" flex={1}>
                  <Text variant="body" fontSize={24}>
                    🌱
                  </Text>
                  <Text
                    variant="body"
                    fontSize={18}
                    fontWeight="bold"
                    color="success"
                  >
                    {treesPlanted}
                  </Text>
                  <Text
                    variant="body"
                    fontSize={12}
                    color="secondaryText"
                    textAlign="center"
                  >
                    Trees Planted
                  </Text>
                </Box>

                <Box alignItems="center" flex={1}>
                  <Text variant="body" fontSize={24}>
                    💨
                  </Text>
                  <Text
                    variant="body"
                    fontSize={18}
                    fontWeight="bold"
                    color="success"
                  >
                    {co2Absorbed}kg
                  </Text>
                  <Text
                    variant="body"
                    fontSize={12}
                    color="secondaryText"
                    textAlign="center"
                  >
                    CO₂ Absorbed/Year
                  </Text>
                </Box>
              </Box>

              <Text
                variant="body"
                fontSize={12}
                color="secondaryText"
                textAlign="center"
                marginTop="s"
              >
                Your contribution helps combat climate change! 🌿
              </Text>
            </Box>
          </MotiView>

          {/* Action Buttons */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Box flexDirection="row" gap="m" marginBottom="l">
              <Box flex={1}>
                <Button
                  label="View Leaderboard"
                  onPress={handleViewLeaderboard}
                  variant="outline"
                />
              </Box>
              <Box flex={1}>
                <Button
                  label="Continue Growing"
                  onPress={handleContinueGrowing}
                />
              </Box>
            </Box>
          </MotiView>

          {/* Motivational Message */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 700 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m">
              <Text
                variant="body"
                fontSize={14}
                color="primaryAction"
                textAlign="center"
                fontWeight="600"
                marginBottom="xs"
              >
                🌟 Keep Growing Your Impact!
              </Text>
              <Text
                variant="body"
                fontSize={12}
                color="secondaryText"
                textAlign="center"
              >
                Continue investing to grow more trees and climb the leaderboard.
                Every contribution makes our planet greener! 🌱
              </Text>
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  );
}
