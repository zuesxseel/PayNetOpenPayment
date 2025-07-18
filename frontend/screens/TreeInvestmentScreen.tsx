"use client";
import { useState, useEffect } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, TouchableOpacity, Image } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Box, Text, Button } from "../components/Themed";
import { useTheme } from "@shopify/restyle";
import { MotiView } from "moti";
import { LinearGradient } from "expo-linear-gradient";
import type { StackNavigationProp } from "@react-navigation/stack";
import type { RouteProp } from "@react-navigation/native";

// Type definitions
type RootStackParamList = {
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
    depositData: DepositData;
    progressGained: number;
  };
  BadgeReward: {
    badge: Badge;
    treesPlanted: number;
    co2Offset: number;
  };
};

type TreeInvestmentScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "TreeInvestment"
>;

type TreeInvestmentScreenRouteProp = RouteProp<
  RootStackParamList,
  "TreeInvestment"
>;

interface TreeInvestmentScreenProps {
  navigation: TreeInvestmentScreenNavigationProp;
  route: TreeInvestmentScreenRouteProp;
}

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
  color: string;
  index: number;
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

const StatCard = ({ icon, label, value, color, index }: StatCardProps) => (
  <MotiView
    from={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ type: "timing", delay: 100 * index }}
  >
    <Box
      backgroundColor="cardPrimaryBackground"
      padding="l"
      borderRadius="m"
      alignItems="center"
    >
      <Feather name={icon as any} size={24} color={color} />
      <Text variant="body" fontSize={14} color="secondaryText" marginTop="s">
        {label}
      </Text>
      <Text variant="body" fontWeight="bold" color="primaryText" marginTop="xs">
        {value}
      </Text>
    </Box>
  </MotiView>
);

export default function TreeInvestmentScreen({
  navigation,
  route,
}: TreeInvestmentScreenProps) {
  const theme = useTheme();

  // User's T+ Tree investment data
  const [investmentData, setInvestmentData] = useState({
    totalDeposit: 2000.0, // Total amount deposited
    totalInterestEarned: 50.32, // Total interest earned so far
    totalDonatedToReforestation: 25.16, // Total donated to tree planting
    daysActive: 45, // Days since first deposit
    progress: 32, // Tree growth progress (0-100%)
    badges: [] as Badge[], // User's earned badges
  });

  // Update investment data when returning from deposit flow
  useEffect(() => {
    if (route.params?.updatedData) {
      setInvestmentData(route.params.updatedData);
    }
  }, [route.params]);

  // Progress calculation: Every RM 100 deposited = 10% progress
  const calculateProgressGain = (depositAmount: number): number => {
    return (depositAmount / 100) * 10; // 10% per RM 100
  };

  // Badge system
  const getBadgeForProgress = (
    progress: number,
    totalDeposit: number
  ): Badge | null => {
    if (progress >= 100) {
      // Determine badge rarity based on total deposit amount
      if (totalDeposit >= 10000) {
        return {
          id: "legendary_forest_guardian",
          name: "Legendary Forest Guardian",
          emoji: "🌲",
          description:
            "You've invested over RM 10,000 and grown a magnificent tree! Your dedication to reforestation is legendary.",
          rarity: "legendary",
          unlockedAt: new Date(),
        };
      } else if (totalDeposit >= 5000) {
        return {
          id: "epic_tree_champion",
          name: "Epic Tree Champion",
          emoji: "🌳",
          description:
            "With over RM 5,000 invested, you've become a true champion of environmental conservation!",
          rarity: "epic",
          unlockedAt: new Date(),
        };
      } else if (totalDeposit >= 2000) {
        return {
          id: "rare_eco_warrior",
          name: "Rare Eco Warrior",
          emoji: "🌿",
          description:
            "Your RM 2,000+ investment shows you're a dedicated warrior for our planet's future!",
          rarity: "rare",
          unlockedAt: new Date(),
        };
      } else {
        return {
          id: "common_tree_grower",
          name: "Tree Grower",
          emoji: "🌱",
          description:
            "Congratulations on growing your first complete tree! Every journey starts with a single seed.",
          rarity: "common",
          unlockedAt: new Date(),
        };
      }
    }
    return null;
  };

  const getTreeStage = (progress: number) => {
    if (progress < 25) return "ground";
    if (progress < 50) return "seedling";
    if (progress < 75) return "sapling";
    return "tree";
  };

  const getTreeImage = (stage: string) => {
    const images: Record<string, any> = {
      ground: require("../assets/Ground.png"),
      seedling: require("../assets/Seedling.png"),
      sapling: require("../assets/Sapling.png"),
      tree: require("../assets/Tree.png"),
    };
    return images[stage];
  };

  const getStageMessage = (stage: string, progress: number) => {
    const messages: Record<string, string> = {
      ground: `Plant your first seed! ${(100 - progress).toFixed(1)}% to go`,
      seedling: `Your seedling is sprouting! ${(100 - progress).toFixed(
        1
      )}% to full growth`,
      sapling: `Growing strong! ${(100 - progress).toFixed(
        1
      )}% until mature tree`,
      tree: "Congratulations! Your tree is fully grown and contributing to reforestation!",
    };
    return messages[stage];
  };

  const handleAddMoney = () => {
    navigation.navigate("AddMoney");
  };

  const handleViewLeaderboard = () => {
    navigation.navigate("TreeLeaderboard");
  };

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box
          flexDirection="row"
          alignItems="center"
          padding="l"
          backgroundColor="cardPrimaryBackground"
        >
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather
              name="arrow-left"
              size={24}
              color={theme.colors.primaryText}
            />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            T+ Tree Investment
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <LinearGradient
              colors={["#00C48C", "#00A651"]}
              style={{
                borderRadius: theme.borderRadii.l,
                padding: theme.spacing.l,
                alignItems: "center",
                marginBottom: theme.spacing.l,
              }}
            >
              <Text
                variant="title2"
                color="primaryActionText"
                textAlign="center"
              >
                🌱 Grow a Tree, Grow the Future
              </Text>
              <Text
                variant="body"
                color="primaryActionText"
                textAlign="center"
                marginTop="s"
                opacity={0.9}
              >
                Your earnings help reforest our planet instead of sitting idle.
              </Text>
            </LinearGradient>
          </MotiView>

          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              backgroundColor="cardPrimaryBackground"
              padding="l"
              borderRadius="l"
              marginBottom="l"
              alignItems="center"
            >
              {/* Tree Growth Stage Image */}
              <Box
                width={200}
                height={200}
                justifyContent="center"
                alignItems="center"
                marginBottom="m"
              >
                <Image
                  source={getTreeImage(getTreeStage(investmentData.progress))}
                  style={{
                    width: 180,
                    height: 180,
                    borderRadius: 20,
                  }}
                  resizeMode="cover"
                />

                {/* Growth stage indicator */}
                <Box
                  position="absolute"
                  bottom={-10}
                  backgroundColor="success"
                  paddingHorizontal="m"
                  paddingVertical="s"
                  borderRadius="m"
                >
                  <Text
                    variant="body"
                    fontSize={12}
                    color="primaryActionText"
                    fontWeight="600"
                  >
                    {getTreeStage(investmentData.progress).toUpperCase()} STAGE
                  </Text>
                </Box>
              </Box>

              {/* Progress bar with milestone markers */}
              <Box width="90%" marginBottom="m">
                <Box
                  flexDirection="row"
                  justifyContent="space-between"
                  marginBottom="s"
                >
                  {[25, 50, 75, 100].map((milestone, index) => (
                    <Box key={milestone} alignItems="center">
                      <Box
                        width={12}
                        height={12}
                        borderRadius="s"
                        backgroundColor={
                          investmentData.progress >= milestone
                            ? "success"
                            : "cardBorder"
                        }
                        marginBottom="xs"
                      />
                      <Text variant="body" fontSize={10} color="secondaryText">
                        {milestone}%
                      </Text>
                    </Box>
                  ))}
                </Box>

                <Box
                  width="100%"
                  height={8}
                  backgroundColor="cardBorder"
                  borderRadius="s"
                  marginBottom="m"
                >
                  <MotiView
                    from={{ width: "0%" }}
                    animate={{ width: `${investmentData.progress}%` }}
                    transition={{ type: "timing", duration: 1000, delay: 500 }}
                  >
                    <Box
                      height="100%"
                      backgroundColor="success"
                      borderRadius="s"
                    />
                  </MotiView>
                </Box>

                {/* Progress percentage display */}
                <Text
                  variant="body"
                  fontWeight="600"
                  color="success"
                  textAlign="center"
                  fontSize={18}
                  marginBottom="s"
                >
                  {investmentData.progress.toFixed(1)}% Complete
                </Text>
              </Box>

              <Text
                variant="body"
                color="secondaryText"
                textAlign="center"
                fontSize={14}
              >
                {getStageMessage(
                  getTreeStage(investmentData.progress),
                  investmentData.progress
                )}
              </Text>
            </Box>
          </MotiView>

          <Box flexDirection="row" gap="m" marginBottom="l">
            <Box flex={1}>
              <StatCard
                icon="dollar-sign"
                label="Total Deposit"
                value={`RM ${investmentData.totalDeposit.toFixed(2)}`}
                color={theme.colors.primaryAction}
                index={0}
              />
            </Box>
            <Box flex={1}>
              <StatCard
                icon="trending-up"
                label="Interest Earned"
                value={`RM ${investmentData.totalInterestEarned.toFixed(2)}`}
                color={theme.colors.success}
                index={1}
              />
            </Box>
          </Box>

          <Box flexDirection="row" gap="m" marginBottom="l">
            <Box flex={1}>
              <StatCard
                icon="globe"
                label="Donated to Trees"
                value={`RM ${investmentData.totalDonatedToReforestation.toFixed(
                  2
                )}`}
                color={theme.colors.treeGreen}
                index={2}
              />
            </Box>
            <Box flex={1}>
              <StatCard
                icon="calendar"
                label="Days Active"
                value={`${investmentData.daysActive} days`}
                color={theme.colors.warning}
                index={3}
              />
            </Box>
          </Box>

          {/* Badges Section */}
          {investmentData.badges.length > 0 && (
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
                >
                  🏆 Your Badges
                </Text>
                <Box flexDirection="row" flexWrap="wrap" gap="s">
                  {investmentData.badges.map((badge, index) => (
                    <Box
                      key={badge.id}
                      backgroundColor="blueLight"
                      padding="s"
                      borderRadius="s"
                      alignItems="center"
                      minWidth={80}
                    >
                      <Text variant="body" fontSize={24} marginBottom="xs">
                        {badge.emoji}
                      </Text>
                      <Text
                        variant="body"
                        fontSize={10}
                        color="primaryAction"
                        fontWeight="600"
                        textAlign="center"
                      >
                        {badge.name}
                      </Text>
                    </Box>
                  ))}
                </Box>
              </Box>
            </MotiView>
          )}

          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
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
                marginBottom="s"
              >
                How T+ Tree Works
              </Text>
              <Text
                variant="body"
                fontSize={14}
                color="secondaryText"
                marginBottom="s"
              >
                • Your balance earns 2.5% annually
              </Text>

              <Text
                variant="body"
                fontSize={14}
                color="secondaryText"
                marginBottom="s"
              >
                • Complete trees (100%) earn you badges
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Track your environmental impact in real-time
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Button
              label="Add More to T+ Tree"
              onPress={handleAddMoney}
              marginBottom="m"
            />
            <Button
              label="View Leaderboard"
              onPress={handleViewLeaderboard}
              variant="outline"
            />
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  );
}
