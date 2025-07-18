"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity, View, StyleSheet, Dimensions } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { LinearGradient } from "expo-linear-gradient"
import { MotiView } from "moti"
import { useState, useEffect } from "react"

const QuickActionButton = ({ icon, label, index, onPress }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <TouchableOpacity onPress={onPress}>
        <Box alignItems="center" gap="s">
          <Box
            width={60}
            height={60}
            borderRadius="xl"
            backgroundColor="cardPrimaryBackground"
            justifyContent="center"
            alignItems="center"
          >
            <Feather name={icon} size={24} color={theme.colors.primaryAction} />
          </Box>
          <Text variant="body" fontSize={14} color="secondaryText">
            {label}
          </Text>
        </Box>
      </TouchableOpacity>
    </MotiView>
  )
}

const TransactionItem = ({ icon, name, type, amount, index }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 200 + 100 * index }}
    >
      <Box flexDirection="row" alignItems="center" paddingVertical="m">
        <Box
          width={44}
          height={44}
          borderRadius="xl"
          backgroundColor="blueLight"
          justifyContent="center"
          alignItems="center"
        >
          <Feather name={icon} size={20} color={theme.colors.primaryAction} />
        </Box>
        <Box flex={1} marginLeft="m">
          <Text variant="body" fontWeight="600" color="primaryText">
            {name}
          </Text>
          <Text variant="body" fontSize={14}>
            {type}
          </Text>
        </Box>
        <Text variant="body" fontWeight="bold" color={amount.startsWith("+") ? "success" : "primaryText"}>
          {amount}
        </Text>
      </Box>
    </MotiView>
  )
}

export default function HomeScreen({ navigation }) {
  const theme = useTheme()
  const { width } = Dimensions.get("window")
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
      <SafeAreaView>
        <ScrollView showsVerticalScrollIndicator={false}>
          <Box>
            <Box flexDirection="row" alignItems="center" justifyContent="space-between" padding="l">
              <Box>
                <Text variant="body" style={{ fontFamily: "Poppins, sans-serif", fontStyle: "italic" }}>
                  Good Morning,
                </Text>
                <Text variant="title1">Asthon Hall</Text>
              </Box>
              <TouchableOpacity onPress={() => navigation.navigate("Notifications")} style={styles.notificationButton}>
                <Feather name="bell" size={24} color={theme.colors.primaryText} />
                {/* Pulsing red dot */}
                <MotiView
                  from={{ scale: 1, opacity: 0.8 }}
                  animate={{ scale: 4, opacity: 0 }}
                  transition={{
                    type: "timing",
                    duration: 2000,
                    loop: true,
                    repeatReverse: false,
                  }}
                  style={[styles.pulseRing, { backgroundColor: "rgba(255, 77, 79, 0.4)" }]}
                />
                <MotiView
                  from={{ scale: 1, opacity: 0.6 }}
                  animate={{ scale: 3, opacity: 0 }}
                  transition={{
                    type: "timing",
                    duration: 2000,
                    loop: true,
                    repeatReverse: false,
                    delay: 500,
                  }}
                  style={[styles.pulseRing, { backgroundColor: "rgba(255, 77, 79, 0.3)" }]}
                />
                <MotiView
                  from={{ scale: 1, opacity: 0.4 }}
                  animate={{ scale: 2, opacity: 0 }}
                  transition={{
                    type: "timing",
                    duration: 2000,
                    loop: true,
                    repeatReverse: false,
                    delay: 1000,
                  }}
                  style={[styles.pulseRing, { backgroundColor: "rgba(255, 77, 79, 0.2)" }]}
                />
                <View style={styles.notificationDot} />
              </TouchableOpacity>
            </Box>
          </Box>
          {/* Animated Total Balance Card */}
          <Box paddingHorizontal="l" marginBottom="l">
            <Box
              height={180}
              borderRadius="xl"
              overflow="hidden"
              style={{
                shadowColor: theme.colors.primaryAction,
                shadowOffset: { width: 0, height: 8 },
                shadowOpacity: 0.2,
                shadowRadius: 12,
                elevation: 10,
              }}
            >
              {/* Exact 90-degree gradient background */}
              <LinearGradient
                colors={[
                  "rgba(16,81,232,1)",
                  "rgba(59,113,237,1)",
                  "rgba(92,136,237,1)",
                  "rgba(130,162,232,1)",
                  "rgba(162,185,235,1)",
                  "rgba(176,195,235,1)",
                  "rgba(206,218,240,1)",
                ]}
                start={{ x: 0, y: 0.5 }}
                end={{ x: 1, y: 0.5 }}
                style={StyleSheet.absoluteFillObject}
              />
              <MotiView
                from={{ translateX: -width }}
                animate={{ translateX: 0 }}
                transition={{
                  type: "timing",
                  duration: 3000,
                  loop: true,
                  repeatReverse: false,
                }}
                style={{
                  ...StyleSheet.absoluteFillObject,
                  backgroundColor: "rgba(255,255,255,0.1)",
                  opacity: 0.5,
                }}
              />
              <MotiView
                from={{ translateX: -width * 0.5 }}
                animate={{ translateX: width * 0.5 }}
                transition={{
                  type: "timing",
                  duration: 4000,
                  loop: true,
                  repeatReverse: false,
                }}
                style={{
                  ...StyleSheet.absoluteFillObject,
                  backgroundColor: "rgba(255,255,255,0.05)",
                  opacity: 0.3,
                  transform: [{ rotateZ: "5deg" }],
                }}
              />
              <Box flex={1} justifyContent="center" padding="l">
                <Text
                  variant="body"
                  opacity={0.8}
                  color="primaryActionText"
                  marginBottom="s"
                  style={{
                    fontFamily: "Poppins, sans-serif",
                  }}
                >
                  Total Balance
                </Text>
                <Text
                  variant="hero"
                  color="primaryActionText"
                  marginVertical="xs"
                  style={{
                    fontSize: 36,
                    fontWeight: "bold",
                    textShadowColor: "rgba(0,0,0,0.2)",
                    textShadowOffset: { width: 1, height: 1 },
                    textShadowRadius: 2,
                    fontFamily: "Poppins, sans-serif",
                  }}
                >
                  RM {displayBalance.toFixed(2)}
                </Text>
                <Box flexDirection="row" alignItems="center" marginTop="xs">
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
          </Box>
          <Box flexDirection="row" justifyContent="space-around" padding="l">
            <QuickActionButton icon="maximize" label="Scan" index={0} onPress={() => navigation.navigate("Scan")} />
            <QuickActionButton icon="arrow-up-right" label="Pay" index={1} onPress={() => {}} />
            <QuickActionButton icon="plus-circle" label="Top Up" index={2} onPress={() => {}} />
            <QuickActionButton
              icon="credit-card"
              label="Add Card"
              index={3}
              onPress={() => navigation.navigate("AccountDetails")}
            />
          </Box>
          <Box paddingHorizontal="l">
            <Box flexDirection="row" justifyContent="space-between" alignItems="center" marginBottom="m" >
              <Text variant="title2" marginRight="m">Recent Activity</Text>
              <TouchableOpacity onPress={() => navigation.navigate("TransactionHistory")}>
                <Box flexDirection="row" alignItems="center" marginTop="xs">
                  <Text variant="body" fontSize={14} color="secondaryText" marginLeft="xs">
                    View Transactions
                  </Text>
                  <Feather name="chevron-right" size={16} marginLeft="s" color={theme.colors.secondaryText} />
                </Box>
              </TouchableOpacity>
            </Box>
            <TransactionItem icon="shopping-cart" name="FamilyMart" type="Payment" amount="- RM 55.50" index={0} />
            <TransactionItem icon="arrow-down-left" name="Top Up" type="e-Wallet" amount="+ RM 100.00" index={1} />
            <TransactionItem icon="coffee" name="Starbucks" type="Payment" amount="- RM 21.00" index={2} />
          </Box>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}

const styles = StyleSheet.create({
  notificationButton: {
    position: "relative",
    padding: 8,
  },
  pulseRing: {
    position: "absolute",
    top: 6,
    right: 6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#FF4D4F",
  },
  notificationDot: {
    position: "absolute",
    top: 6,
    right: 6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#FF4D4F",
    zIndex: 1,
  },
})
