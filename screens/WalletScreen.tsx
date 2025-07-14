"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const InfoCard = ({ label, value, icon, index, onPress }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <TouchableOpacity onPress={onPress}>
        <Box
          flexDirection="row"
          alignItems="center"
          backgroundColor="cardPrimaryBackground"
          padding="l"
          borderRadius="m"
        >
          <Box
            width={50}
            height={50}
            backgroundColor="blueLight"
            borderRadius="xl"
            justifyContent="center"
            alignItems="center"
          >
            <Feather name={icon} size={24} color={theme.colors.primaryAction} />
          </Box>
          <Box flex={1} marginLeft="m">
            <Text variant="body" fontSize={14} color="secondaryText">
              {label}
            </Text>
            <Text variant="body" fontWeight="600" color="primaryText" marginTop="xs">
              {value}
            </Text>
          </Box>
          <Feather name="chevron-right" size={20} color="#6B7280" />
        </Box>
      </TouchableOpacity>
    </MotiView>
  )
}

export default function WalletScreen({ navigation }) {
  const theme = useTheme()

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box padding="l" backgroundColor="cardPrimaryBackground">
          <Text variant="title1">My Wallet</Text>
        </Box>
        <ScrollView contentContainerStyle={{ padding: theme.spacing.l, gap: theme.spacing.m }}>
          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing" }}
          >
            <Box alignItems="center" paddingVertical="xl" backgroundColor="cardPrimaryBackground" borderRadius="l">
              <Text variant="body" color="secondaryText">
                Available Balance
              </Text>
              <Text variant="hero" color="primaryText" marginTop="s">
                RM 1,234.56
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box flexDirection="row" gap="m">
              <Box flex={1}>
                <Button label="Top Up" onPress={() => {}} />
              </Box>
              <Box flex={1}>
                <Button label="Withdraw" onPress={() => {}} variant="outline" />
              </Box>
            </Box>
          </MotiView>

          <InfoCard
            label="T+ Tree Investment"
            value="RM 50.32 • Growing 🌱"
            icon="trending-up"
            index={0}
            onPress={() => navigation.navigate("TreeInvestment")}
          />
          <InfoCard label="Saved Cards" value="Visa **** 4567" icon="credit-card" index={1} onPress={() => {}} />
          <InfoCard
            label="Transaction History"
            value="View all statements"
            icon="file-text"
            index={2}
            onPress={() => navigation.navigate("TransactionHistory")}
          />
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
