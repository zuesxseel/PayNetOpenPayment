"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const TransactionItem = ({ transaction, index }) => {
  const getNetworkColor = (type: string) => {
    const colors: Record<string, string> = {
      DuitNow: "#FF6B35",
      PayNow: "#00A651",
      UPI: "#FF9933",
      PromptPay: "#1E88E5",
      QRIS: "#E53E3E",
    }
    return colors[type] || "#0A57E7"
  }

  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <Box
        flexDirection="row"
        alignItems="center"
        backgroundColor="cardPrimaryBackground"
        padding="m"
        borderRadius="m"
        marginBottom="s"
      >
        <Box
          width={44}
          height={44}
          borderRadius="xl"
          backgroundColor={transaction.type === "credit" ? "greenLight" : "blueLight"}
          justifyContent="center"
          alignItems="center"
        >
          <Feather
            name={transaction.type === "credit" ? "arrow-down-left" : "arrow-up-right"}
            size={20}
            color={transaction.type === "credit" ? "#00C48C" : "#0A57E7"}
          />
        </Box>
        <Box flex={1} marginLeft="m">
          <Text variant="body" fontWeight="600" color="primaryText">
            {transaction.merchant}
          </Text>
          <Text variant="body" fontSize={14} color="secondaryText">
            {transaction.network} • {transaction.date}
          </Text>
          {transaction.savings && (
            <Text variant="body" fontSize={12} style={{ color: "#00C48C" }}>
              Saved RM {transaction.savings}
            </Text>
          )}
        </Box>
        <Box alignItems="flex-end">
          <Text
            variant="body"
            fontWeight="bold"
            style={{ color: transaction.type === "credit" ? "#00C48C" : "#0C0D0F" }}
            fontSize={16}
          >
            {transaction.type === "credit" ? "+" : "-"} {transaction.currency} {transaction.amount}
          </Text>
          {transaction.network !== "DuitNow" && (
            <Box
              style={{ backgroundColor: getNetworkColor(transaction.network) }}
              paddingHorizontal="s"
              paddingVertical="xs"
              borderRadius="s"
              marginTop="xs"
            >
              <Text variant="body" fontSize={10} color="primaryActionText">
                {transaction.network}
              </Text>
            </Box>
          )}
        </Box>
      </Box>
    </MotiView>
  )
}

export default function TransactionHistoryScreen({ navigation }: { navigation: any }) {
  const theme = useTheme()

  const transactions = [
    {
      id: 1,
      merchant: "FamilyMart Bukit Bintang",
      amount: "55.50",
      currency: "MYR",
      network: "DuitNow",
      type: "debit",
      date: "Today, 2:30 PM",
      savings: null,
    },
    {
      id: 2,
      merchant: "Starbucks Marina Bay",
      amount: "25.00",
      currency: "SGD",
      network: "PayNow",
      type: "debit",
      date: "Yesterday, 10:15 AM",
      savings: "3.20",
    },
    {
      id: 3,
      merchant: "Delhi Street Food",
      amount: "450.00",
      currency: "INR",
      network: "UPI",
      type: "debit",
      date: "Dec 20, 6:45 PM",
      savings: "8.50",
    },
    {
      id: 4,
      merchant: "Top Up",
      amount: "100.00",
      currency: "MYR",
      network: "DuitNow",
      type: "credit",
      date: "Dec 19, 9:00 AM",
      savings: null,
    },
    {
      id: 5,
      merchant: "7-Eleven Bangkok",
      amount: "120.00",
      currency: "THB",
      network: "PromptPay",
      type: "debit",
      date: "Dec 18, 3:20 PM",
      savings: "2.80",
    },
  ]

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Transaction History
          </Text>
        </Box>
        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          <MotiView
            from={{ opacity: 0, translateY: -10 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="body" color="secondaryText" marginBottom="s">
                Total Cross-Border Savings This Month
              </Text>
              <Text variant="title2" style={{ color: "#00C48C" }}>
                RM 14.50
              </Text>
            </Box>
          </MotiView>

          {transactions.map((transaction, index) => (
            <TransactionItem key={transaction.id} transaction={transaction} index={index} />
          ))}
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
