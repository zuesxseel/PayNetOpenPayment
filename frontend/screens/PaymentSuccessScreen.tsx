"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function PaymentSuccessScreen({ route, navigation }) {
  const theme = useTheme()
  const { qrData } = route.params

  const getNetworkInfo = (type) => {
    const networks = {
      DuitNow: { color: theme.colors.duitNowOrange, country: "Malaysia", route: "DuitNow → PayNow" },
      PayNow: { color: theme.colors.payNowGreen, country: "Singapore", route: "PayNow → DuitNow" },
      UPI: { color: theme.colors.upiOrange, country: "India", route: "UPI → DuitNow" },
      PromptPay: { color: theme.colors.promptPayBlue, country: "Thailand", route: "PromptPay → DuitNow" },
      QRIS: { color: theme.colors.qrisRed, country: "Indonesia", route: "QRIS → PayNow" },
    }
    return networks[type] || { color: theme.colors.primaryAction, country: "Unknown", route: "Direct" }
  }

  const networkInfo = getNetworkInfo(qrData.type)
  const fxSavings = (Math.random() * 10 + 2).toFixed(2) // Random savings between 2-12

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <ScrollView 
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ flexGrow: 1, justifyContent: "center", padding: 24 }}
        >
          <Box alignItems="stretch" width="100%">
            <MotiView
              from={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "timing", duration: 500 }}
            >
              <Box alignItems="center" marginBottom="l">
                <Box
                  width={100}
                  height={100}
                  backgroundColor="success"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                >
                  <Feather name="check" size={50} color={theme.colors.primaryActionText} />
                </Box>
              </Box>
            </MotiView>

            <MotiView
              from={{ translateY: 20, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Text variant="title1" textAlign="center" marginBottom="s">
                Payment Successful!
              </Text>
              <Text variant="body" textAlign="center" marginBottom="xl">
                Your cross-border payment has been processed successfully.
              </Text>
            </MotiView>

            <MotiView
              from={{ translateY: 30, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 400 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" width="100%" marginBottom="l">
                <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                  <Text variant="body" color="secondaryText">
                    Merchant
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="600">
                    {qrData.merchantName}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                  <Text variant="body" color="secondaryText">
                    Amount Paid
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="600">
                    {qrData.currency} {qrData.amount}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                  <Text variant="body" color="secondaryText">
                    Smart Route
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="600">
                    {networkInfo.route}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    FX Savings
                  </Text>
                  <Text variant="body" color="success" fontWeight="600">
                    RM {fxSavings} saved
                  </Text>
                </Box>
              </Box>
            </MotiView>

            <MotiView
              from={{ translateY: 50, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 600 }}
            >
              <Box backgroundColor="success" padding="m" borderRadius="m" marginBottom="l" width="100%">
                <Text variant="body" color="primaryActionText" textAlign="center" fontWeight="600">
                  🌱 RM 0.50 contributed to T+ Tree reforestation
                </Text>
              </Box>
            </MotiView>

            <MotiView
              from={{ translateY: 50, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 800 }}
            >
              <Box width="100%">
                <Button label="Back to Home" onPress={() => navigation.navigate("Home")} />
              </Box>
            </MotiView>
          </Box>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
