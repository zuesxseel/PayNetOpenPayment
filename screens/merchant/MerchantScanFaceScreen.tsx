"use client"
import { useState, useEffect } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Dimensions } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const { width } = Dimensions.get("window")

export default function MerchantScanFaceScreen({ navigation }) {
  const theme = useTheme()
  const [isScanning, setIsScanning] = useState(true)
  const [customerData, setCustomerData] = useState(null)

  useEffect(() => {
    // Simulate face recognition after 3 seconds
    const timer = setTimeout(() => {
      setIsScanning(false)
      setCustomerData({
        name: "Sarah Chen",
        walletId: "GrabPay: ID12345",
        country: "🇲🇾",
        confidence: 98,
        walletType: "GrabPay",
        kycVerified: true,
        lastSeen: "2 days ago",
      })
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  const handleConfirmCustomer = () => {
    navigation.navigate("MerchantEnterAmount", { customerData })
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Face Recognition
          </Text>
        </Box>

        <Box flex={1} justifyContent="center" alignItems="center" padding="l">
          {/* Camera Viewport */}
          <MotiView
            from={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box
              width={width - 80}
              height={width - 80}
              backgroundColor="cardPrimaryBackground"
              borderRadius="xl"
              justifyContent="center"
              alignItems="center"
              marginBottom="l"
              borderWidth={3}
              borderColor={isScanning ? "warning" : "success"}
            >
              {isScanning ? (
                <MotiView
                  from={{ scale: 1 }}
                  animate={{ scale: 1.1 }}
                  transition={{ type: "timing", duration: 1000, loop: true }}
                >
                  <Box
                    width={200}
                    height={200}
                    borderRadius="xl"
                    backgroundColor="blueLight"
                    justifyContent="center"
                    alignItems="center"
                    borderWidth={2}
                    borderColor="primaryAction"
                  >
                    <Feather name="user" size={80} color={theme.colors.primaryAction} />
                  </Box>
                </MotiView>
              ) : (
                <MotiView
                  from={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "timing", duration: 500 }}
                >
                  <Box
                    width={200}
                    height={200}
                    borderRadius="xl"
                    backgroundColor="greenLight"
                    justifyContent="center"
                    alignItems="center"
                    borderWidth={2}
                    borderColor="success"
                  >
                    <Feather name="user-check" size={80} color={theme.colors.success} />
                  </Box>
                </MotiView>
              )}
            </Box>
          </MotiView>

          {isScanning ? (
            <MotiView from={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ type: "timing", delay: 200 }}>
              <Text variant="title2" textAlign="center" marginBottom="s">
                Scanning Face...
              </Text>
              <Text variant="body" textAlign="center" color="secondaryText">
                Matching identity from wallet KYC database
              </Text>
            </MotiView>
          ) : (
            <MotiView
              from={{ translateY: 20, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", duration: 500 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" width="100%" marginBottom="l">
                <Box flexDirection="row" alignItems="center" marginBottom="m">
                  <Feather name="check-circle" size={24} color={theme.colors.success} />
                  <Text variant="title2" marginLeft="m" color="success">
                    Identity Confirmed
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Customer Name
                  </Text>
                  <Text variant="body" fontWeight="600" color="primaryText">
                    {customerData?.name}
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Wallet ID
                  </Text>
                  <Text variant="body" fontWeight="600" color="primaryText">
                    {customerData?.walletId}
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Country
                  </Text>
                  <Text variant="body" fontWeight="600" color="primaryText">
                    {customerData?.country} Malaysia
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Confidence Score
                  </Text>
                  <Text variant="body" fontWeight="600" color="success">
                    {customerData?.confidence}%
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    KYC Status
                  </Text>
                  <Box flexDirection="row" alignItems="center">
                    <Feather name="shield-check" size={16} color={theme.colors.success} />
                    <Text variant="body" fontWeight="600" color="success" marginLeft="xs">
                      Verified
                    </Text>
                  </Box>
                </Box>
              </Box>

              <Button label="Confirm Customer" onPress={handleConfirmCustomer} />
            </MotiView>
          )}
        </Box>
      </SafeAreaView>
    </Box>
  )
}
