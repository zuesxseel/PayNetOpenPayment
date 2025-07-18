"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../../components/Themed"
import { useTheme } from "@shopify/restyle"
import { LinearGradient } from "expo-linear-gradient"
import { MotiView } from "moti"

const StatCard = ({ icon, label, value, color, index }) => (
  <MotiView
    from={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ type: "timing", delay: 100 * index }}
  >
    <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" alignItems="center" flex={1}>
      <Feather name={icon} size={24} color={color} />
      <Text variant="body" fontSize={14} color="secondaryText" marginTop="s">
        {label}
      </Text>
      <Text variant="body" fontWeight="bold" color="primaryText" marginTop="xs">
        {value}
      </Text>
    </Box>
  </MotiView>
)

const TransactionItem = ({ transaction, index }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 200 + 100 * index }}
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
          backgroundColor="success"
          justifyContent="center"
          alignItems="center"
        >
          <Feather name="user-check" size={20} color={theme.colors.primaryActionText} />
        </Box>
        <Box flex={1} marginLeft="m">
          <Text variant="body" fontWeight="600" color="primaryText">
            {transaction.customerName}
          </Text>
          <Text variant="body" fontSize={14} color="secondaryText">
            {transaction.method} • {transaction.time}
          </Text>
        </Box>
        <Box alignItems="flex-end">
          <Text variant="body" fontWeight="bold" color="success" fontSize={16}>
            +RM {transaction.amount}
          </Text>
          <Text variant="body" fontSize={12} color="secondaryText">
            Risk: {transaction.riskScore}%
          </Text>
        </Box>
      </Box>
    </MotiView>
  )
}

export default function MerchantDashboardScreen({ navigation }) {
  const theme = useTheme()

  const recentTransactions = [
    {
      id: 1,
      customerName: "Sarah Chen",
      amount: "45.80",
      method: "Face + PIN",
      time: "2 mins ago",
      riskScore: 12,
    },
    {
      id: 2,
      customerName: "Ahmad Rahman",
      amount: "23.50",
      method: "Face + PIN",
      time: "15 mins ago",  
      riskScore: 8,
    },
    {
      id: 3,
      customerName: "Priya Sharma",
      amount: "67.20",
      method: "Face + PIN",
      time: "1 hour ago",
      riskScore: 15,
    },
  ]

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <ScrollView showsVerticalScrollIndicator={false}>
          <Box padding="l">
            <Box flexDirection="row" justifyContent="space-between" alignItems="center" marginBottom="l">
              <Box>
                <Text variant="body" color="secondaryText">
                  Good morning,
                </Text>
                <Text variant="title1">FamilyMart Bukit Bintang</Text>
              </Box>
              <TouchableOpacity onPress={() => navigation.navigate("MerchantSettings")}>
                <Feather name="settings" size={24} color={theme.colors.secondaryText} />
              </TouchableOpacity>
            </Box>

            <MotiView
              from={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "timing" }}
            >
              <LinearGradient
                colors={[theme.colors.gradientStart, theme.colors.gradientEnd]}
                style={{ borderRadius: theme.borderRadii.l, padding: theme.spacing.l, marginBottom: theme.spacing.l }}
              >
                <Text variant="body" color="primaryActionText" opacity={0.8}>
                  Today's Revenue
                </Text>
                <Text variant="hero" color="primaryActionText" marginVertical="s">
                  RM 2,847.60
                </Text>
                <Text variant="body" color="primaryActionText" opacity={0.8}>
                  +12.5% from yesterday
                </Text>
              </LinearGradient>
            </MotiView>

            <MotiView
              from={{ translateY: 20, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Button
                label="🔍 Start Face-to-Pay"
                onPress={() => navigation.navigate("MerchantScanFace")}
                marginBottom="l"
              />
            </MotiView>

            <Box flexDirection="row" gap="m" marginBottom="l">
              <StatCard icon="users" label="Customers Today" value="47" color={theme.colors.primaryAction} index={0} />
              <StatCard icon="shield-check" label="Avg Risk Score" value="11%" color={theme.colors.success} index={1} />
            </Box>

            <Box flexDirection="row" gap="m" marginBottom="l">
              <StatCard icon="clock" label="Avg Transaction" value="8.2s" color={theme.colors.warning} index={2} />
              <StatCard
                icon="trending-up"
                label="Success Rate"
                value="99.2%"
                color={theme.colors.treeGreen}
                index={3}
              />
            </Box>

            <Text variant="title2" marginBottom="m">
              Recent Transactions
            </Text>
            {recentTransactions.map((transaction, index) => (
              <TransactionItem key={transaction.id} transaction={transaction} index={index} />
            ))}
          </Box>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
