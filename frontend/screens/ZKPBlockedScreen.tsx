"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Alert } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { useState } from "react"

interface ZKPBlockedScreenProps {
  navigation: any
  route: any
}

export default function ZKPBlockedScreen({ navigation, route }: ZKPBlockedScreenProps) {
  const theme = useTheme()
  const { notification } = route.params || {}
  const [isWalletFrozen, setIsWalletFrozen] = useState(false)

  const handleFreezeWallet = () => {
    if (isWalletFrozen) {
      // Unfreeze wallet
      Alert.alert(
        "Unfreeze Wallet",
        "Are you sure you want to unfreeze your wallet? This will allow all transactions to proceed normally.",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Unfreeze",
            onPress: () => {
              setIsWalletFrozen(false)
              Alert.alert("Wallet Unfrozen", "Your wallet has been unfrozen. You can now make transactions normally.", [
                { text: "OK" },
              ])
            },
          },
        ],
      )
    } else {
      // Freeze wallet
      Alert.alert(
        "Freeze Wallet",
        "Are you sure you want to freeze your wallet? This will block all transactions until you unfreeze it.",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Freeze",
            style: "destructive",
            onPress: () => {
              setIsWalletFrozen(true)
              Alert.alert(
                "Wallet Frozen",
                "Your wallet has been frozen for security. You can unfreeze it anytime from this screen.",
                [{ text: "OK" }],
              )
            },
          },
        ],
      )
    }
  }

  const handleImAware = () => {
    Alert.alert(
      "Acknowledged",
      "Thank you for confirming. We'll continue monitoring your account for suspicious activity.",
      [{ text: "OK", onPress: () => navigation.navigate("Home") }],
    )
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title2" marginLeft="m" color="primaryText">
            Security Alert
          </Text>
        </Box>

        <Box flex={1} paddingHorizontal="l">
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Box marginBottom="l">
              <Text variant="title1" color="primaryText" marginBottom="s">
                We blocked a payment
              </Text>
              <Text variant="body" color="secondaryText" fontSize={16} lineHeight={24}>
                Someone failed to verify their identity through Zero-Knowledge Proof.
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="m">
              <Box flexDirection="row" alignItems="flex-start" marginBottom="l">
                <Box
                  width={48}
                  height={48}
                  borderRadius="m"
                  backgroundColor="blueLight"
                  justifyContent="center"
                  alignItems="center"
                  marginRight="m"
                >
                  <Feather name="smartphone" size={24} color={theme.colors.primaryAction} />
                </Box>
                <Box flex={1}>
                  <Text variant="body" fontWeight="600" color="primaryText" marginBottom="xs">
                    Payment attempt from {notification?.device || "Unknown Device"}
                  </Text>
                  <Text variant="body" color="secondaryText" marginBottom="xs">
                    {notification?.location || "Da Nang, Vietnam"}
                  </Text>
                  <Text variant="body" fontSize={14} color="secondaryText">
                    Today at{" "}
                    {new Date().toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                      hour12: false,
                    })}
                  </Text>
                </Box>
              </Box>

              <Box flexDirection="row" alignItems="center" backgroundColor="dangerLight" padding="m" borderRadius="s">
                <Box
                  width={24}
                  height={24}
                  borderRadius="xl"
                  backgroundColor="error"
                  justifyContent="center"
                  alignItems="center"
                  marginRight="m"
                >
                  <Feather name="x" size={12} color="white" />
                </Box>
                <Text variant="body" fontSize={14} color="error" flex={1}>
                  Prevented on {new Date().toLocaleDateString("en-GB")} at{" "}
                  {new Date().toLocaleTimeString("en-US", {
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                  })}
                </Text>
              </Box>
            </Box>
          </MotiView>

          {notification && (
            <MotiView
              from={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "timing", delay: 400 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="m">
                <Text variant="body" fontWeight="600" color="primaryText" marginBottom="m">
                  Transaction Details
                </Text>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Merchant
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="500">
                    {notification.merchant}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Amount
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="500">
                    {notification.amount}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    Transaction ID
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="500" fontSize={12}>
                    {notification.transactionId || "TXN-" + Math.random().toString(36).substr(2, 9).toUpperCase()}
                  </Text>
                </Box>
              </Box>
            </MotiView>
          )}

          {/* Wallet Status Indicator */}
          {isWalletFrozen && (
            <MotiView
              from={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "timing" }}
            >
              <Box
                backgroundColor="warningLight"
                padding="m"
                borderRadius="m"
                marginBottom="l"
                flexDirection="row"
                alignItems="center"
              >
                <Feather name="alert-circle" size={20} color={theme.colors.warning} style={{ marginRight: 8 }} />
                <Text variant="body" color="warning" fontWeight="500" flexShrink={1}>
                  Wallet is currently frozen
                </Text>
              </Box>
            </MotiView>
          )}

        {/* Action Buttons */}
          <Box paddingBottom="l">
            <MotiView
              from={{ opacity: 0, translateY: 20 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ type: "timing", delay: 800 }}
            >
              <Box flexDirection="row" style={{ gap: 12 }}>
                {/* I'm Aware Button - Left */}
                <Box flex={1}>
                  <TouchableOpacity onPress={handleImAware}>
                    <Box
                      backgroundColor="cardSecondaryBackground"
                      paddingVertical="l"
                      paddingHorizontal="m"
                      borderRadius="m"
                      alignItems="center"
                      borderWidth={2}
                      borderColor="cardBorder"
                      flexDirection="row"
                      justifyContent="center"
                      minHeight={56}
                    >
                      <Feather name="check-circle" size={18} color={theme.colors.secondaryText} />
                      <Text
                        variant="body"
                        color="secondaryText"
                        fontWeight="600"
                        fontSize={15}
                        marginLeft="xs"
                        textAlign="center"
                        numberOfLines={1}
                        adjustsFontSizeToFit
                      >
                        I'm aware
                      </Text>
                    </Box>
                  </TouchableOpacity>
                </Box>

                {/* Freeze/Unfreeze Wallet Button - Right */}
                <Box flex={1}>
                  <TouchableOpacity onPress={handleFreezeWallet}>
                    <MotiView
                      from={{ backgroundColor: isWalletFrozen ? theme.colors.success : theme.colors.error }}
                      animate={{ backgroundColor: isWalletFrozen ? theme.colors.success : theme.colors.error }}
                      transition={{ type: "timing", duration: 300 }}
                      style={{
                        borderRadius: theme.borderRadii.m,
                        paddingVertical: theme.spacing.l,
                        paddingHorizontal: theme.spacing.m,
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                        minHeight: 56,
                        shadowColor: isWalletFrozen ? "#52C41A" : "#FF4D4F",
                        shadowOffset: { width: 0, height: 4 },
                        shadowOpacity: 0.3,
                        shadowRadius: 8,
                        elevation: 8,
                      }}
                    >
                      <Feather name={isWalletFrozen ? "unlock" : "lock"} size={18} color="white" />
                      <Text
                        variant="body"
                        color="primaryActionText"
                        fontWeight="700"
                        fontSize={15}
                        marginLeft="xs"
                        textAlign="center"
                        numberOfLines={1}
                        adjustsFontSizeToFit
                      >
                        {isWalletFrozen ? "Unfreeze" : "Freeze Wallet"}
                      </Text>
                    </MotiView>
                  </TouchableOpacity>
                </Box>
              </Box>
            </MotiView>
          </Box>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
