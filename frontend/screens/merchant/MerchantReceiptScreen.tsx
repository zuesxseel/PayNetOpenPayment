"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity, Alert } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function MerchantReceiptScreen({ route, navigation }) {
  const theme = useTheme()
  const { transactionData } = route.params

  const formatDateTime = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleString("en-MY", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getRiskColor = (score) => {
    if (score < 15) return theme.colors.success
    if (score < 25) return theme.colors.warning
    return theme.colors.error
  }

  const getRiskLabel = (score) => {
    if (score < 15) return "Low"
    if (score < 25) return "Medium"
    return "High"
  }

  const handleSendReceipt = () => {
    Alert.alert("Send Receipt", "Choose how to send the receipt to customer:", [
      { text: "WhatsApp", onPress: () => Alert.alert("Receipt sent via WhatsApp!") },
      { text: "Email", onPress: () => Alert.alert("Receipt sent via Email!") },
      { text: "Cancel", style: "cancel" },
    ])
  }

  const handleNewTransaction = () => {
    navigation.navigate("MerchantDashboard")
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.navigate("MerchantDashboard")}>
            <Feather name="home" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Transaction Receipt
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: 24 }}>
          {/* Success Header */}
          <MotiView
            from={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box alignItems="center" marginBottom="l">
              <Box
                width={80}
                height={80}
                backgroundColor="success"
                borderRadius="xl"
                justifyContent="center"
                alignItems="center"
                marginBottom="m"
              >
                <Feather name="check" size={40} color={theme.colors.primaryActionText} />
              </Box>
              <Text variant="title1" color="success" textAlign="center">
                Payment Successful!
              </Text>
              <Text variant="body" color="secondaryText" textAlign="center" marginTop="s">
                Transaction ID: {transactionData.id}
              </Text>
            </Box>
          </MotiView>

          {/* Receipt Details */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="title2" marginBottom="m" textAlign="center">
                Receipt Details
              </Text>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Customer Name
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {transactionData.customerData.name}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Wallet Used
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {transactionData.customerData.walletType}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Payment Amount
                </Text>
                <Text variant="title2" color="primaryText">
                  {transactionData.currency} {transactionData.amount.toFixed(2)}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Merchant Fee
                </Text>
                <Text variant="body" color="secondaryText">
                  -{transactionData.currency} {transactionData.merchantFee.toFixed(2)}
                </Text>
              </Box>

              <Box height={1} backgroundColor="cardBorder" marginVertical="m" />

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" fontWeight="600" color="primaryText">
                  Net Amount
                </Text>
                <Text variant="title2" color="success">
                  {transactionData.currency} {(transactionData.amount - transactionData.merchantFee).toFixed(2)}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Auth Method
                </Text>
                <Box flexDirection="row" alignItems="center">
                  <Feather name="shield-check" size={16} color={theme.colors.success} />
                  <Text variant="body" fontWeight="600" color="primaryText" marginLeft="xs">
                    {transactionData.method}
                  </Text>
                </Box>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Risk Score
                </Text>
                <Text variant="body" fontWeight="600" color={getRiskColor(transactionData.riskScore)}>
                  {getRiskLabel(transactionData.riskScore)} ({transactionData.riskScore}%)
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="m">
                <Text variant="body" color="secondaryText">
                  Date & Time
                </Text>
                <Text variant="body" color="primaryText">
                  {formatDateTime(transactionData.timestamp)}
                </Text>
              </Box>

              {transactionData.fxRate !== 1.0 && (
                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    FX Rate
                  </Text>
                  <Text variant="body" color="primaryText">
                    1.00 = {transactionData.fxRate.toFixed(4)}
                  </Text>
                </Box>
              )}
            </Box>
          </MotiView>

          {/* AI Insights */}
          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="blueLight" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center" marginBottom="s">
                <Feather name="cpu" size={20} color={theme.colors.primaryAction} />
                <Text variant="body" fontWeight="600" color="primaryAction" marginLeft="s">
                  AI Security Analysis
                </Text>
              </Box>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Face recognition confidence: {transactionData.customerData.confidence}%
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Device fingerprint: Trusted
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Transaction pattern: Normal
              </Text>
            </Box>
          </MotiView>

          {/* Action Buttons */}
          <MotiView
            from={{ opacity: 0, translateY: 40 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Button label="📱 Send Receipt to Customer" onPress={handleSendReceipt} marginBottom="m" />
            <Button label="New Transaction" onPress={handleNewTransaction} variant="outline" />
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
