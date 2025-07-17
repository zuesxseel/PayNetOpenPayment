"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const FeatureItem = ({ icon, title, description, index }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <Box flexDirection="row" alignItems="center" marginBottom="l">
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
          <Text variant="body" fontWeight="600" color="primaryText">
            {title}
          </Text>
          <Text variant="body" fontSize={14} color="secondaryText" marginTop="xs">
            {description}
          </Text>
        </Box>
      </Box>
    </MotiView>
  )
}

export default function RegisterStartScreen({ navigation }) {
  const theme = useTheme()

  const handleGoBack = () => {
    navigation.goBack()
  }

  const handleStartKYC = () => {
    navigation.navigate("ScanIC")
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <Box flex={1} backgroundColor="mainBackground">
        {/* Header with back button */}
        <Box padding="l" paddingBottom="m">
          <TouchableOpacity onPress={handleGoBack}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
        </Box>

        {/* Scrollable content */}
        <ScrollView 
          style={{ flex: 1 }} 
          contentContainerStyle={{ paddingHorizontal: 24, paddingBottom: 20 }}
          showsVerticalScrollIndicator={false}
        >
          <MotiView
            from={{ translateY: -20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing" }}
          >
            <Box alignItems="center" marginBottom="xl">
              <Box
                width={80}
                height={80}
                backgroundColor="success"
                borderRadius="xl"
                justifyContent="center"
                alignItems="center"
                marginBottom="l"
              >
                <Feather name="shield" size={40} color={theme.colors.primaryActionText} />
              </Box>
              <Text variant="title1" textAlign="center" marginBottom="s">
                Create Your Account
              </Text>
              <Text variant="body" textAlign="center" color="secondaryText">
                Complete our secure eKYC verification to get started with Open Payment
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="title2" marginBottom="m">
                What You'll Need
              </Text>

              <FeatureItem
                icon="credit-card"
                title="Malaysian IC (MyKad)"
                description="We'll scan your ID to verify your identity"
                index={0}
              />

              <FeatureItem
                icon="camera"
                title="Live Selfie"
                description="Take a selfie to confirm it's really you"
                index={1}
              />

              <FeatureItem
                icon="cpu"
                title="AI Verification"
                description="Our system will verify your documents instantly"
                index={2}
              />
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 30, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center">
                <Feather name="shield" size={20} color={theme.colors.primaryAction} />
                <Text variant="body" fontSize={14} color="primaryAction" marginLeft="s" fontWeight="600">
                  Your data is encrypted and secure
                </Text>
              </Box>
              <Text variant="body" fontSize={12} color="secondaryText" marginTop="xs">
                We use bank-level security to protect your personal information
              </Text>
            </Box>
          </MotiView>
        </ScrollView>

        {/* Fixed bottom button */}
        <Box padding="l" backgroundColor="mainBackground">
          <MotiView
            from={{ translateY: 50, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Button label="Start eKYC Verification" onPress={handleStartKYC} />
          </MotiView>
        </Box>
      </Box>
    </SafeAreaView>
  )
}
