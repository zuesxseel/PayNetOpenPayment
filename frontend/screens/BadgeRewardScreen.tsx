"use client";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, TouchableOpacity } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Box, Text, Button } from "../components/Themed";
import { useTheme } from "@shopify/restyle";
import { MotiView } from "moti";
import { LinearGradient } from "expo-linear-gradient";
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
  TreeLeaderboard: undefined;
};

type BadgeRewardScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "BadgeReward"
>;

type BadgeRewardScreenRouteProp = RouteProp<RootStackParamList, "BadgeReward">;

interface BadgeRewardScreenProps {
  navigation: BadgeRewardScreenNavigationProp;
  route: BadgeRewardScreenRouteProp;
}

interface Badge {
  id: string;
  name: string;
  emoji: string;
  description: string;
  rarity: "common" | "rare" | "epic" | "legendary";
  unlockedAt: Date;
}

export default function BadgeRewardScreen({
  navigation,
  route,
}: BadgeRewardScreenProps) {
  const theme = useTheme();
  const { badge, treesPlanted, co2Offset } = route.params;

  // For theme-compatible color keys (used in themed components)
  const getRarityThemeColor = (rarity: Badge["rarity"]) => {
    switch (rarity) {
      case "common":
        return "secondaryText" as const;
      case "rare":
        return "primaryAction" as const;
      case "epic":
        return "warning" as const;
      case "legendary":
        return "warning" as const;
      default:
        return "primaryAction" as const;
    }
  };

  // For raw color values (used in LinearGradient and style props)
  const getRarityGradient = (rarity: Badge["rarity"]) => {
    const gradients: Record<Badge["rarity"], [string, string]> = {
      common: [
        theme.colors.secondaryText as string,
        theme.colors.cardBorder as string,
      ],
      rare: [
        theme.colors.primaryAction as string,
        theme.colors.gradientEnd as string,
      ],
      epic: [theme.colors.warning as string, theme.colors.error as string],
      legendary: [
        theme.colors.warning as string,
        theme.colors.success as string,
      ],
    };
    return gradients[rarity];
  };

  const handleContinueJourney = () => {
    // Reset the navigation stack to remove badge/deposit screens from history
    navigation.reset({
      index: 1,
      routes: [
        { name: "WalletHome" },
        {
          name: "TreeInvestment",
          params: { updatedData: route.params.updatedInvestmentData },
        },
      ],
    });
  };

  const handleViewLeaderboard = () => {
    navigation.navigate("TreeLeaderboard");
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
          <TouchableOpacity onPress={handleContinueJourney}>
            <Feather
              name="arrow-left"
              size={24}
              color={theme.colors.primaryText}
            />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Badge Earned!
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          <MotiView
            from={{ scale: 0.5, opacity: 0, rotateY: "180deg" }}
            animate={{ scale: 1, opacity: 1, rotateY: "0deg" }}
            transition={{ type: "timing", duration: 800 }}
          >
            <LinearGradient
              colors={getRarityGradient(badge.rarity)}
              style={{
                borderRadius: theme.borderRadii.l,
                padding: theme.spacing.m,
                width: "100%",
                alignItems: "center",
                marginBottom: theme.spacing.l,
              }}
            >
              {/* Celebration Header */}
              <MotiView
                from={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "timing", duration: 600, delay: 400 }}
              >
                <Text
                  variant="title1"
                  color="primaryActionText"
                  textAlign="center"
                  marginBottom="s"
                >
                  🎉 CONGRATS! 🎉
                </Text>
              </MotiView>

              <Text
                variant="title1"
                color="primaryActionText"
                textAlign="center"
                marginBottom="m"
              >
                Your Tree is Fully Grown!
              </Text>

              {/* Badge Display */}
              <MotiView
                from={{ scale: 0, rotateZ: "0deg" }}
                animate={{ scale: 1, rotateZ: "360deg" }}
                transition={{ type: "timing", duration: 1000, delay: 600 }}
              >
                <Box
                  width={100}
                  height={100}
                  backgroundColor="primaryActionText"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                  marginBottom="m"
                  borderWidth={4}
                  borderColor={getRarityThemeColor(badge.rarity)}
                >
                  <Text variant="hero" fontSize={50}>
                    {badge.emoji}
                  </Text>
                </Box>
              </MotiView>

              {/* Badge Info */}
              <Box
                backgroundColor="primaryActionText"
                padding="m"
                borderRadius="m"
                width="100%"
                marginBottom="m"
              >
                <Text
                  variant="title2"
                  textAlign="center"
                  marginBottom="s"
                  color="primaryText"
                >
                  {badge.name}
                </Text>

                <Box
                  backgroundColor={getRarityThemeColor(badge.rarity)}
                  paddingHorizontal="m"
                  paddingVertical="s"
                  borderRadius="s"
                  alignSelf="center"
                  marginBottom="m"
                >
                  <Text
                    variant="body"
                    fontSize={12}
                    fontWeight="600"
                    color="primaryActionText"
                    textTransform="uppercase"
                  >
                    {badge.rarity} BADGE
                  </Text>
                </Box>

                <Text
                  variant="body"
                  fontSize={14}
                  color="secondaryText"
                  textAlign="center"
                  marginBottom="l"
                >
                  {badge.description}
                </Text>

                {/* Achievement Stats */}
                <Box
                  backgroundColor="mainBackground"
                  padding="m"
                  borderRadius="s"
                >
                  <Text
                    variant="body"
                    fontWeight="600"
                    color="primaryText"
                    textAlign="center"
                    marginBottom="s"
                  >
                    🌍 Your Environmental Impact
                  </Text>

                  <Box flexDirection="row" justifyContent="space-around">
                    <Box alignItems="center">
                      <Text variant="body" fontSize={24}>
                        🌳
                      </Text>
                      <Text
                        variant="body"
                        fontWeight="bold"
                        color="success"
                        fontSize={18}
                      >
                        {treesPlanted}
                      </Text>
                      <Text variant="body" fontSize={12} color="secondaryText">
                        Trees Funded
                      </Text>
                    </Box>

                    <Box alignItems="center">
                      <Text variant="body" fontSize={24}>
                        💨
                      </Text>
                      <Text
                        variant="body"
                        fontWeight="bold"
                        color="success"
                        fontSize={18}
                      >
                        {co2Offset}kg
                      </Text>
                      <Text variant="body" fontSize={12} color="secondaryText">
                        CO₂ Offset
                      </Text>
                    </Box>

                    <Box alignItems="center">
                      <Text variant="body" fontSize={24}>
                        🏆
                      </Text>
                      <Text
                        variant="body"
                        fontWeight="bold"
                        color="warning"
                        fontSize={18}
                      >
                        100%
                      </Text>
                      <Text variant="body" fontSize={12} color="secondaryText">
                        Complete
                      </Text>
                    </Box>
                  </Box>
                </Box>
              </Box>

              {/* Motivational Message */}
              <Box
                backgroundColor="primaryActionText"
                padding="m"
                borderRadius="s"
                marginBottom="m"
                width="100%"
              >
                <Text
                  variant="body"
                  fontSize={14}
                  color="success"
                  textAlign="center"
                  fontWeight="600"
                >
                  🌟 You're making a real difference for our planet!
                </Text>
                <Text
                  variant="body"
                  fontSize={12}
                  color="secondaryText"
                  textAlign="center"
                  marginTop="xs"
                >
                  Keep growing more trees to earn additional badges and multiply
                  your impact!
                </Text>
              </Box>
            </LinearGradient>
          </MotiView>

          {/* Action Buttons */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 1000 }}
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
                  label="Continue Journey"
                  onPress={handleContinueJourney}
                />
              </Box>
            </Box>
          </MotiView>

          {/* Achievement Message */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 1100 }}
          >
            <Box
              backgroundColor="cardPrimaryBackground"
              padding="l"
              borderRadius="m"
            >
              <Text
                variant="body"
                fontWeight="600"
                color="primaryText"
                textAlign="center"
                marginBottom="s"
              >
                🚀 Ready for the Next Challenge?
              </Text>
              <Text
                variant="body"
                fontSize={14}
                color="secondaryText"
                textAlign="center"
              >
                Your tree has reached full maturity! Start a new tree and work
                towards earning even rarer badges. The planet needs more
                champions like you!
              </Text>
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  );
}
