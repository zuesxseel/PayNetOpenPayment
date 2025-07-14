"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { LinearGradient } from "expo-linear-gradient"

const StatCard = ({ icon, label, value, color, index }) => (
  <MotiView
    from={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ type: "timing", delay: 100 * index }}
  >
    <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" alignItems="center">
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

export default function TreeInvestmentScreen({ navigation }) {
  const theme = useTheme()
  const progress = 32 // 32% progress

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            T+ Tree Investment
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: theme.spacing.l }}>
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <LinearGradient
              colors={["#00C48C", "#00A651"]}
              style={{
                borderRadius: theme.borderRadii.l,
                padding: theme.spacing.l,
                alignItems: "center",
                marginBottom: theme.spacing.l,
              }}
            >
              <Text variant="title2" color="primaryActionText" textAlign="center">
                🌱 Grow a Tree, Grow the Future
              </Text>
              <Text variant="body" color="primaryActionText" textAlign="center" marginTop="s" opacity={0.9}>
                Your earnings help reforest our planet instead of sitting idle.
              </Text>
            </LinearGradient>
          </MotiView>

          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              backgroundColor="cardPrimaryBackground"
              padding="l"
              borderRadius="l"
              marginBottom="l"
              alignItems="center"
            >
              {/* Simple Tree SVG representation */}
              <Box width={120} height={120} justifyContent="center" alignItems="center" marginBottom="m">
                <Box
                  width={8}
                  height={40}
                  backgroundColor="treeTrunk"
                  position="absolute"
                  bottom={0}
                  borderRadius="s"
                />
                <Box
                  width={progress * 0.8}
                  height={progress * 0.8}
                  backgroundColor="success"
                  borderRadius="xl"
                  position="absolute"
                  top={20}
                />
                <Box
                  width={progress * 0.6}
                  height={progress * 0.6}
                  backgroundColor="treeGreen"
                  borderRadius="xl"
                  position="absolute"
                  top={30}
                  left={-10}
                />
                <Box
                  width={progress * 0.6}
                  height={progress * 0.6}
                  backgroundColor="treeGreen"
                  borderRadius="xl"
                  position="absolute"
                  top={30}
                  right={-10}
                />
              </Box>

              <Box width="80%" height={8} backgroundColor="cardBorder" borderRadius="s" marginBottom="m">
                <Box width={`${progress}%`} height="100%" backgroundColor="success" borderRadius="s" />
              </Box>

              <Text variant="body" color="secondaryText" textAlign="center">
                Your tree will fully sprout when you reach RM 10 earned
              </Text>
            </Box>
          </MotiView>

          <Box flexDirection="row" gap="m" marginBottom="l">
            <Box flex={1}>
              <StatCard
                icon="dollar-sign"
                label="Total Earned"
                value="RM 50.32"
                color={theme.colors.success}
                index={0}
              />
            </Box>
            <Box flex={1}>
              <StatCard
                icon="trending-up"
                label="Progress"
                value={`${progress}%`}
                color={theme.colors.primaryAction}
                index={1}
              />
            </Box>
          </Box>

          <Box flexDirection="row" gap="m" marginBottom="l">
            <Box flex={1}>
              <StatCard icon="calendar" label="Days Active" value="45 days" color={theme.colors.warning} index={2} />
            </Box>
            <Box flex={1}>
              <StatCard icon="globe" label="Trees Funded" value="0.3 trees" color={theme.colors.treeGreen} index={3} />
            </Box>
          </Box>

          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="body" fontWeight="600" color="primaryText" marginBottom="s">
                How T+ Tree Works
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Your balance earns 2.5% annually
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Earnings are pooled with other users
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Funds are donated to verified reforestation partners
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Track your environmental impact in real-time
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Button label="Add More to T+ Tree" onPress={() => {}} marginBottom="m" />
            <Button label="View Forest Impact" onPress={() => {}} variant="outline" />
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
