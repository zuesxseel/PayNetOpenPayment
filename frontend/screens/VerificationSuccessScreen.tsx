"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { useAuth } from "../context/AuthContext"
import { MotiView } from "moti"

export default function VerificationSuccessScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  const { registrationData } = route.params

  const handleContinueToLogin = () => {
    // Navigate to welcome page where users can choose login type
    navigation.navigate("Welcome")
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flex={1} justifyContent="center" alignItems="center" padding="l">
          <MotiView
            from={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box
              width={120}
              height={120}
              backgroundColor="success"
              borderRadius="xl"
              justifyContent="center"
              alignItems="center"
              marginBottom="l"
            >
              <Feather name="check" size={60} color={theme.colors.primaryActionText} />
            </Box>
          </MotiView>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Text variant="hero" textAlign="center" marginBottom="s" color="success">
              Verification Successful!
            </Text>
            <Text variant="body" textAlign="center" marginBottom="xl" color="secondaryText">
              Your identity has been verified successfully. Your Open Payment account is now ready to use!
            </Text>
          </MotiView>

          <MotiView
            from={{ translateY: 30, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l" width="100%">
              <Text variant="title2" textAlign="center" marginBottom="m">
                Account Summary
              </Text>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  Account Holder
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {registrationData.icData.name}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  NRIC
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {registrationData.icData.nric}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  Email
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {registrationData.contactInfo.email}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  Phone
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {registrationData.contactInfo.phone}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between">
                <Text variant="body" color="secondaryText">
                  Verification Status
                </Text>
                <Box flexDirection="row" alignItems="center">
                  <Text variant="body" fontWeight="600" color="success" marginLeft="xs">
                    Verified
                  </Text>
                </Box>
              </Box>
            </Box>
          </MotiView>
        </Box>

        {/* Fixed bottom button */}
        <Box padding="l" backgroundColor="mainBackground">
          <MotiView
            from={{ translateY: 50, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Button 
              label="Continue to Login" 
              onPress={handleContinueToLogin} 
              paddingHorizontal="l" 
            />
          </MotiView>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
