"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity, StyleSheet, Dimensions } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { LinearGradient } from "expo-linear-gradient"
import { useState, useEffect } from "react"
const { width } = Dimensions.get("window")

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
    const targetBalance = 1234.56
    const [displayBalance, setDisplayBalance] = useState(0)

    useEffect(() => {
      let start = 0
      const duration = 600 // milliseconds
      const increment = targetBalance / (duration / 16) // ~60 frames per second

      const animateCount = () => {
        start += increment
        if (start < targetBalance) {
          setDisplayBalance(Number.parseFloat(start.toFixed(2)))
          requestAnimationFrame(animateCount)
        } else {
          setDisplayBalance(targetBalance)
        }
      }

      requestAnimationFrame(animateCount)
    }, [targetBalance])
  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box padding="l" backgroundColor="cardPrimaryBackground">
          <Text variant="title1">My Wallet</Text>
        </Box>
        <ScrollView contentContainerStyle={{ padding: theme.spacing.l, gap: theme.spacing.m }}>
          {/* Available Balance Card with Apple Black Space Gradient */}
          <Box
            height={180}
            borderRadius="xl"
            overflow="hidden"
            style={{
              shadowColor: theme.colors.primaryText,
              shadowOffset: { width: 0, height: 8 },
              shadowOpacity: 0.2,
              shadowRadius: 12,
              elevation: 10,
            }}
          >
            <LinearGradient
              colors={["#1C1B1B", "#121212", "#1A1A1A", "#262626", "#1C1C1E"]}  
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={StyleSheet.absoluteFillObject}
            />
            {/* Twinkling Stars */}
              {[...Array(3)].map((_, i) => (
                <MotiView
                  key={i}
                  from={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1.2 }}
                  transition={{
                    type: "timing",
                    duration: 1000 + i * 200,
                    loop: true,
                    repeatReverse: true,
                    delay: i * 300,
                  }}
                  style={{
                    position: "absolute",
                    width: 4 + i * 2, // Varying star sizes
                    height: 4 + i * 2,
                    borderRadius: (4 + i * 2) / 2,
                    backgroundColor: "rgba(255,255,255,0.8)",
                    top: `${Math.random() * 80 + 10}%`, // Random positions
                    left: `${Math.random() * 80 + 10}%`,
                    zIndex: 1,
                  }}
                />
              ))}

            <Box flex={1} zIndex={2} justifyContent="center" padding="l">
              <Text variant="body" color="primaryActionText" opacity={0.8}>
                Available Balance
              </Text>
              <Text variant="hero" color="primaryActionText" marginTop="m">
                RM {displayBalance.toFixed(2)}
              </Text>
                <Box flexDirection="row" alignItems="center" marginTop="m">
                  <Box
                    width={8}
                    height={8}
                    backgroundColor="primaryActionText"
                    opacity={0.75}
                    marginRight="s"
                    style={{ borderRadius: 999 }}
                    />
                  <Text
                    fontSize={14}
                    color="primaryActionText"
                    style={{
                      fontFamily: "Poppins, sans-serif",
                      fontWeight: "500",
                      opacity: 0.8,
                    }}
                    >
                    Green+ 🌱
                  </Text>
                </Box>
            </Box>
          </Box>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box flexDirection="row" gap="m">
              <Box flex={1} position="relative">
           
                <TouchableOpacity onPress={() => {}}>
                  <Box
                    backgroundColor="primaryAction"
                    paddingVertical="m"
                    borderRadius="l"
                    alignItems="center"
                    flexDirection="row"
                    justifyContent="center"
                  >
                    <Text variant="button" color="primaryActionText" justifyContent="center">
                      Top Up
                    </Text>
                    <Feather name="plus-circle" size={18} color="white" style={{ marginRight: -8, marginLeft: 8 }} />
                  </Box>
                </TouchableOpacity>
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
