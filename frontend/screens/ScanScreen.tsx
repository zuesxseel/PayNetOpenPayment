"use client"

import { useState } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TextInput } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function ScanScreen({ navigation }) {
  const theme = useTheme()
  const [qrPayload, setQrPayload] = useState(
    '{"type":"DuitNow","merchantId":"MERCH123","amount":55.50,"currency":"MYR","merchantName":"FamilyMart Bukit Bintang"}',
  )

  const handleScan = () => {
    // Parse QR and navigate to processing
    try {
      const parsedData = JSON.parse(qrPayload)
      navigation.navigate("PaymentProcessing", { qrData: parsedData })
    } catch (error) {
      // Handle invalid QR
      console.log("Invalid QR format")
    }
  }

  const handleUploadQR = () => {
    // Simulate different QR types
    const qrTypes = [
      {
        type: "PayNow",
        merchantId: "SG_MERCH456",
        amount: 25.0,
        currency: "SGD",
        merchantName: "Starbucks Marina Bay",
      },
      {
        type: "UPI",
        merchantId: "merchant@paytm",
        amount: 450.0,
        currency: "INR",
        merchantName: "Delhi Street Food",
      },
      {
        type: "PromptPay",
        merchantId: "TH_SHOP789",
        amount: 120.0,
        currency: "THB",
        merchantName: "7-Eleven Bangkok",
      },
    ]

    const randomQR = qrTypes[Math.floor(Math.random() * qrTypes.length)]
    setQrPayload(JSON.stringify(randomQR, null, 2))
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flex={1} justifyContent="center" padding="l">
          <MotiView
            from={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box alignItems="center" marginBottom="xl">
              <Box
                width={80}
                height={80}
                backgroundColor="primaryAction"
                borderRadius="xl"
                justifyContent="center"
                alignItems="center"
              >
                <Feather name="maximize" size={40} color={theme.colors.primaryActionText} />
              </Box>
              <Text variant="title1" textAlign="center" marginTop="l">
                QR Scanner
              </Text>
              <Text variant="body" textAlign="center" marginTop="m">
                Scan any QR code from DuitNow, PayNow, UPI, PromptPay, or QRIS networks.
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              backgroundColor="cardPrimaryBackground"
              borderRadius="m"
              padding="m"
              borderWidth={1}
              borderColor="cardBorder"
            >
              <Text variant="body" marginBottom="s" color="primaryText">
                Sample QR Payload (JSON)
              </Text>
              <TextInput
                value={qrPayload}
                onChangeText={setQrPayload}
                multiline
                style={{
                  backgroundColor: theme.colors.mainBackground,
                  padding: theme.spacing.m,
                  borderRadius: theme.borderRadii.m,
                  fontSize: 14,
                  fontFamily: "monospace",
                  minHeight: 120,
                  textAlignVertical: "top",
                }}
              />
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 50, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box flexDirection="row" gap="m" marginTop="l">
              <Box flex={1}>
                <Button label="Upload QR" onPress={handleUploadQR} variant="outline" />
              </Box>
              <Box flex={1}>
                <Button label="Scan & Pay" onPress={handleScan} />
              </Box>
            </Box>
          </MotiView>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
