"use client"
import { useState } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, TextInput, Alert } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function MerchantEnterAmountScreen({ route, navigation }) {
  const theme = useTheme()
  const { customerData } = route.params
  const [amount, setAmount] = useState("")
  const [pin, setPin] = useState("")
  const [pinAttempts, setPinAttempts] = useState(0)
  const [showPinEntry, setShowPinEntry] = useState(false)

  const handleAmountSubmit = () => {
    if (!amount || Number.parseFloat(amount) <= 0) {
      Alert.alert("Invalid Amount", "Please enter a valid payment amount")
      return
    }
    setShowPinEntry(true)
  }

  const handlePinSubmit = () => {
    // Simulate PIN verification
    const correctPin = "123456" // Mock PIN

    if (pin === correctPin) {
      // Generate transaction data
      const transactionData = {
        id: `TXN_${Date.now()}`,
        customerData,
        amount: Number.parseFloat(amount),
        currency: "MYR",
        method: "Face + PIN",
        timestamp: new Date().toISOString(),
        riskScore: Math.floor(Math.random() * 20) + 5, // 5-25%
        fxRate: 1.0,
        merchantFee: Number.parseFloat(amount) * 0.015, // 1.5% fee
      }

      navigation.navigate("MerchantReceipt", { transactionData })
    } else {
      setPinAttempts((prev) => prev + 1)
      setPin("")

      if (pinAttempts >= 2) {
        Alert.alert("PIN Verification Failed", "Maximum attempts reached. Transaction cancelled.", [
          { text: "OK", onPress: () => navigation.goBack() },
        ])
      } else {
        Alert.alert("Incorrect PIN", `${2 - pinAttempts} attempts remaining`)
      }
    }
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Enter Amount
          </Text>
        </Box>

        <Box flex={1} padding="l">
          {/* Customer Info Card */}
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center" marginBottom="m">
                <Box
                  width={50}
                  height={50}
                  backgroundColor="success"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                >
                  <Feather name="user-check" size={24} color={theme.colors.primaryActionText} />
                </Box>
                <Box marginLeft="m">
                  <Text variant="body" fontWeight="600" color="primaryText">
                    {customerData.name}
                  </Text>
                  <Text variant="body" fontSize={14} color="secondaryText">
                    {customerData.walletId}
                  </Text>
                </Box>
              </Box>
            </Box>
          </MotiView>

          {!showPinEntry ? (
            <MotiView
              from={{ opacity: 0, translateY: 20 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
                <Text variant="title2" marginBottom="m">
                  Payment Amount
                </Text>
                <Box flexDirection="row" alignItems="center" marginBottom="l">
                  <Text variant="hero" color="primaryText" marginRight="s">
                    RM
                  </Text>
                  <TextInput
                    value={amount}
                    onChangeText={setAmount}
                    placeholder="0.00"
                    keyboardType="decimal-pad"
                    style={{
                      flex: 1,
                      fontSize: 36,
                      fontWeight: "bold",
                      color: theme.colors.primaryText,
                    }}
                  />
                </Box>
              </Box>
              <Button label="Continue to PIN Entry" onPress={handleAmountSubmit} />
            </MotiView>
          ) : (
            <MotiView
              from={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "timing", duration: 500 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
                <Text variant="title2" marginBottom="m" textAlign="center">
                  Customer PIN Entry
                </Text>
                <Text variant="body" color="secondaryText" textAlign="center" marginBottom="l">
                  Ask customer to enter their 6-digit PIN
                </Text>

                <Box alignItems="center" marginBottom="l">
                  <Text variant="hero" color="primaryText" marginBottom="m">
                    RM {amount}
                  </Text>

                  <Box flexDirection="row" gap="s" marginBottom="l">
                    {[...Array(6)].map((_, index) => (
                      <Box
                        key={index}
                        width={40}
                        height={40}
                        backgroundColor={index < pin.length ? "primaryAction" : "cardBorder"}
                        borderRadius="s"
                        justifyContent="center"
                        alignItems="center"
                      >
                        {index < pin.length && (
                          <Text variant="body" color="primaryActionText" fontWeight="bold">
                            •
                          </Text>
                        )}
                      </Box>
                    ))}
                  </Box>

                  <TextInput
                    value={pin}
                    onChangeText={setPin}
                    placeholder="Enter PIN (123456 for demo)"
                    secureTextEntry
                    keyboardType="numeric"
                    maxLength={6}
                    style={{
                      width: "100%",
                      height: 50,
                      backgroundColor: theme.colors.mainBackground,
                      borderRadius: theme.borderRadii.m,
                      paddingHorizontal: theme.spacing.m,
                      fontSize: 16,
                      textAlign: "center",
                    }}
                  />
                </Box>

                <Box backgroundColor="warning" padding="s" borderRadius="s" marginBottom="m">
                  <Text variant="body" fontSize={12} color="primaryActionText" textAlign="center">
                    🔒 PIN is hashed client-side • Max 3 attempts • Demo PIN: 123456
                  </Text>
                </Box>
              </Box>

              <Button label="Verify PIN & Complete Payment" onPress={handlePinSubmit} disabled={pin.length !== 6} />
            </MotiView>
          )}
        </Box>
      </SafeAreaView>
    </Box>
  )
}
