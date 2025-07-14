"use client"
import { useEffect } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function PaymentProcessingScreen({ route, navigation }) {
  const theme = useTheme()
  const { qrData } = route.params

  useEffect(() => {
    // Simulate processing time
    const timer = setTimeout(() => {
      navigation.replace("PaymentSuccess", { qrData })
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  const getNetworkColor = (type) => {
    const colors = {
      DuitNow: theme.colors.duitNowOrange,
      PayNow: theme.colors.payNowGreen,
      UPI: theme.colors.upiOrange,
      PromptPay: theme.colors.promptPayBlue,
      QRIS: theme.colors.qrisRed,
    }
    return colors[type] || theme.colors.primaryAction
  }

  return (
    <Box flex={1} backgroundColor="mainBackground" justifyContent="center" alignItems="center" padding="l">
      <SafeAreaView style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <MotiView
          from={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "timing", duration: 500 }}
        >
          <Box
            width={100}
            height={100}
            backgroundColor="cardPrimaryBackground"
            borderRadius="xl"
            justifyContent="center"
            alignItems="center"
            marginBottom="l"
          >
            <MotiView
              from={{ rotate: "0deg" }}
              animate={{ rotate: "360deg" }}
              transition={{ type: "timing", duration: 2000, loop: true }}
            >
              <Feather name="loader" size={50} color={getNetworkColor(qrData.type)} />
            </MotiView>
          </Box>
        </MotiView>

        <Text variant="title1" textAlign="center" marginBottom="m">
          Processing Payment
        </Text>
        <Text variant="body" textAlign="center" marginBottom="l">
          Connecting to {qrData.type} network...
        </Text>

        <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" width="100%">
          <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
            <Text variant="body" color="secondaryText">
              Merchant
            </Text>
            <Text variant="body" color="primaryText" fontWeight="600">
              {qrData.merchantName}
            </Text>
          </Box>
          <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
            <Text variant="body" color="secondaryText">
              Amount
            </Text>
            <Text variant="body" color="primaryText" fontWeight="600">
              {qrData.currency} {qrData.amount}
            </Text>
          </Box>
          <Box flexDirection="row" justifyContent="space-between">
            <Text variant="body" color="secondaryText">
              Network
            </Text>
            <Text variant="body" color="primaryText" fontWeight="600">
              {qrData.type}
            </Text>
          </Box>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
