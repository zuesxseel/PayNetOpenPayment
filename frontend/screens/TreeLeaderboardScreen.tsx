"use client";
import { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, TouchableOpacity, Image, View } from "react-native";
import { Feather } from "@expo/vector-icons";
import { Box, Text } from "../components/Themed";
import { useTheme } from "@shopify/restyle";
import { MotiView } from "moti";
import { LinearGradient } from "expo-linear-gradient";
import { StackNavigationProp } from "@react-navigation/stack";

// Type definitions
type RootStackParamList = {
  TreeLeaderboard: undefined;
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
  // Add other screen names as needed
};

type TreeLeaderboardScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "TreeLeaderboard"
>;

interface TreeLeaderboardScreenProps {
  navigation: TreeLeaderboardScreenNavigationProp;
}

interface User {
  rank: number;
  name: string;
  treesFunded: number;
  totalDonated: string;
  daysActive: number;
  co2Offset: number;
}

interface LeaderboardItemProps {
  user: User;
  index: number;
  isCurrentUser?: boolean;
}

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
  color: string;
  index: number;
}

const LeaderboardItem = ({
  user,
  index,
  isCurrentUser = false,
}: LeaderboardItemProps) => {
  const theme = useTheme();

  const getRankIcon = (rank: number) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  const getRankColor = (rank: number) => {
    if (rank === 1) return "#FFD700"; // Gold
    if (rank === 2) return "#C0C0C0"; // Silver
    if (rank === 3) return "#CD7F32"; // Bronze
    return theme.colors.secondaryText;
  };

  const getTreeBadge = (treeCount: number) => {
    if (treeCount >= 100)
      return {
        emoji: "🌳",
        title: "Forest Guardian",
        color: "treeGreen" as const,
      };
    if (treeCount >= 50)
      return {
        emoji: "🌲",
        title: "Tree Champion",
        color: "success" as const,
      };
    if (treeCount >= 20)
      return {
        emoji: "🌿",
        title: "Green Warrior",
        color: "primaryAction" as const,
      };
    if (treeCount >= 5)
      return { emoji: "🌱", title: "Eco Starter", color: "warning" as const };
    return {
      emoji: "🌾",
      title: "Seed Planter",
      color: "secondaryText" as const,
    };
  };

  const badge = getTreeBadge(user.treesFunded);

  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <Box
        backgroundColor={isCurrentUser ? "blueLight" : "cardPrimaryBackground"}
        padding="l"
        borderRadius="m"
        marginBottom="s"
        borderWidth={isCurrentUser ? 2 : 0}
        {...(isCurrentUser ? { borderColor: "primaryAction" } : {})}
      >
        <Box flexDirection="row" alignItems="center">
          {/* Rank */}
          {user.rank <= 3 ? (
            <View
              style={{
                width: 50,
                height: 50,
                borderRadius: 25,
                backgroundColor: getRankColor(user.rank),
                justifyContent: "center",
                alignItems: "center",
                marginRight: theme.spacing.m,
              }}
            >
              <Text
                variant="body"
                fontSize={20}
                fontWeight="bold"
                color="primaryActionText"
              >
                {getRankIcon(user.rank)}
              </Text>
            </View>
          ) : (
            <Box
              width={50}
              height={50}
              borderRadius="xl"
              backgroundColor="mainBackground"
              justifyContent="center"
              alignItems="center"
              marginRight="m"
            >
              <Text
                variant="body"
                fontSize={16}
                fontWeight="bold"
                color="primaryText"
              >
                #{user.rank}
              </Text>
            </Box>
          )}

          {/* User Info */}
          <Box flex={1}>
            <Box flexDirection="row" alignItems="center" marginBottom="xs">
              <Text variant="body" fontWeight="600" color="primaryText">
                {user.name}
                {isCurrentUser && (
                  <Text variant="body" fontSize={12} color="primaryAction">
                    {" "}
                    (You)
                  </Text>
                )}
              </Text>
            </Box>

            <Box
              flexDirection="row"
              alignItems="center"
              justifyContent="space-between"
            >
              <Box flexDirection="row" alignItems="center">
                <Text
                  variant="body"
                  fontSize={12}
                  color={badge.color}
                  marginRight="xs"
                >
                  {badge.emoji}
                </Text>
                <Text variant="body" fontSize={12} color="secondaryText">
                  {badge.title}
                </Text>
              </Box>

              <Box flexDirection="row" alignItems="center">
                <Feather name="globe" size={16} color={theme.colors.success} />
                <Text
                  variant="body"
                  fontWeight="bold"
                  color="success"
                  marginLeft="xs"
                >
                  {user.treesFunded} trees
                </Text>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Additional Stats for Top 3 */}
        {user.rank <= 3 && (
          <Box
            backgroundColor="mainBackground"
            padding="s"
            borderRadius="s"
            marginTop="m"
            flexDirection="row"
            justifyContent="space-around"
          >
            <Box alignItems="center">
              <Text variant="body" fontSize={12} color="secondaryText">
                Donated
              </Text>
              <Text
                variant="body"
                fontSize={14}
                fontWeight="600"
                color="success"
              >
                RM {user.totalDonated}
              </Text>
            </Box>
            <Box alignItems="center">
              <Text variant="body" fontSize={12} color="secondaryText">
                Days Active
              </Text>
              <Text
                variant="body"
                fontSize={14}
                fontWeight="600"
                color="primaryText"
              >
                {user.daysActive}
              </Text>
            </Box>
            <Box alignItems="center">
              <Text variant="body" fontSize={12} color="secondaryText">
                CO₂ Offset
              </Text>
              <Text
                variant="body"
                fontSize={14}
                fontWeight="600"
                color="treeGreen"
              >
                {user.co2Offset}kg
              </Text>
            </Box>
          </Box>
        )}
      </Box>
    </MotiView>
  );
};

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
      flex={1}
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

export default function TreeLeaderboardScreen({
  navigation,
}: TreeLeaderboardScreenProps) {
  const theme = useTheme();
  const [timeFilter, setTimeFilter] = useState("all"); // all, month, week

  // Mock leaderboard data
  const leaderboardData = [
    {
      rank: 1,
      name: "S***** C***",
      treesFunded: 127,
      totalDonated: "2,540.00",
      daysActive: 89,
      co2Offset: 3175,
    },
    {
      rank: 2,
      name: "A***** R*****",
      treesFunded: 98,
      totalDonated: "1,960.00",
      daysActive: 76,
      co2Offset: 2450,
    },
    {
      rank: 3,
      name: "P***** S*****",
      treesFunded: 84,
      totalDonated: "1,680.00",
      daysActive: 65,
      co2Offset: 2100,
    },
    {
      rank: 4,
      name: "D***** L*****",
      treesFunded: 67,
      totalDonated: "1,340.00",
      daysActive: 54,
      co2Offset: 1675,
    },
    {
      rank: 5,
      name: "M***** S*****",
      treesFunded: 52,
      totalDonated: "1,040.00",
      daysActive: 43,
      co2Offset: 1300,
    },
    {
      rank: 6,
      name: "N**** H***** S****", // Current user
      treesFunded: 23,
      totalDonated: "460.00",
      daysActive: 45,
      co2Offset: 575,
    },
    {
      rank: 7,
      name: "J***** W*****",
      treesFunded: 19,
      totalDonated: "380.00",
      daysActive: 32,
      co2Offset: 475,
    },
    {
      rank: 8,
      name: "R***** P*****",
      treesFunded: 15,
      totalDonated: "300.00",
      daysActive: 28,
      co2Offset: 375,
    },
  ];

  const currentUser = leaderboardData.find(
    (user) => user.name === "A***** L*****"
  );
  const totalTrees = leaderboardData.reduce(
    (sum, user) => sum + user.treesFunded,
    0
  );
  const totalCO2 = leaderboardData.reduce(
    (sum, user) => sum + user.co2Offset,
    0
  );

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
            Tree Leaderboard
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          {/* Your Rank Card */}
          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              backgroundColor="primaryAction"
              padding="l"
              borderRadius="m"
              marginBottom="l"
            >
              <Box
                flexDirection="row"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Text variant="body" color="primaryActionText" opacity={0.8}>
                    Your Current Rank
                  </Text>
                  <Text variant="title2" color="primaryActionText">
                    #{currentUser?.rank} of {leaderboardData.length}
                  </Text>
                </Box>
                <Box alignItems="center">
                  <Text variant="hero" color="primaryActionText">
                    🌱
                  </Text>
                  <Text
                    variant="body"
                    fontSize={12}
                    color="primaryActionText"
                    opacity={0.8}
                  >
                    {currentUser?.treesFunded} trees
                  </Text>
                </Box>
              </Box>
            </Box>
          </MotiView>

          {/* Leaderboard List */}
          <Text variant="title2" marginBottom="m">
            🏆 Top Contributors
          </Text>

          {leaderboardData.map((user, index) => (
            <LeaderboardItem
              key={user.rank}
              user={user}
              index={index}
              isCurrentUser={user.name === "A***** L*****"}
            />
          ))}

          {/* Motivational Footer */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Box
              backgroundColor="greenLight"
              padding="l"
              borderRadius="m"
              marginTop="l"
            >
              <Text
                variant="body"
                fontWeight="600"
                color="success"
                textAlign="center"
                marginBottom="s"
              >
                🎯 Climb the Leaderboard!
              </Text>
              <Text
                variant="body"
                fontSize={14}
                color="secondaryText"
                textAlign="center"
              >
                Increase your T+ Tree deposits to fund more trees and rise in
                the rankings. Every tree makes a difference!
              </Text>
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  );
}
