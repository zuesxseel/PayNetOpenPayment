"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const VerificationLog = ({ message, status, index }: { message: string; status: string; index: number }) => {
  const theme = useTheme()
  const getStatusIcon = () => {
    switch (status) {
      case "success":
        return "check-circle"
      case "error":
        return "x-circle"
      default:
        return "clock"
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case "success":
        return theme.colors.success
      case "error":
        return theme.colors.error
      default:
        return theme.colors.secondaryText
    }
  }

  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <Box flexDirection="row" alignItems="center" marginBottom="m">
        <Feather name={getStatusIcon()} size={16} color={getStatusColor()} />
        <Text variant="body" fontSize={14} color="primaryText" marginLeft="m" flex={1}>
          {message}
        </Text>
      </Box>
    </MotiView>
  )
}

export default function VerificationFailedScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  const { registrationData } = route.params

  const failedVerificationSteps = [
    { message: "Initializing verification engine...", status: "success" },
    { message: "ID image received. Extracting text from ID...", status: "success" },
    {
      message: `Extracted Name: ${registrationData.icData.name}, NRIC: ${registrationData.icData.nric}`,
      status: "success",
    },
    { message: "Verifying ID card authenticity (hologram, layout, etc.)...", status: "error" },
    { message: "ID document validity check failed - suspicious patterns detected.", status: "error" },
    { message: "Performing facial recognition match...", status: "error" },
    { message: "Comparing live selfie to ID photo...", status: "error" },
    { message: "Face match failed (42% confidence) - insufficient similarity.", status: "error" },
    { message: "Conducting liveness check on selfie...", status: "error" },
    { message: "Liveness check failed - potential spoofing detected.", status: "error" },
    { message: "Connecting to national identity database...", status: "success" },
    { message: "Cross-checking NRIC and personal details with government records...", status: "error" },
    { message: "Personal details mismatch with official records.", status: "error" },
    { message: "Verification failed - multiple checks did not pass.", status: "error" },
  ]

  const handleRetry = () => {
    // Navigate back to AI verification with incremented attempt count
    navigation.navigate("AIVerification", { 
      registrationData, 
      verificationAttempt: 2 
    })
  }

  const handleContactSupport = () => {
    // In a real app, this would open support chat or email
    alert("Support contact feature would be implemented here")
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Verification Failed
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: 24 }}>
          <MotiView
            from={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box alignItems="center" marginBottom="l">
              <Box
                width={120}
                height={120}
                backgroundColor="error"
                borderRadius="xl"
                justifyContent="center"
                alignItems="center"
                marginBottom="l"
              >
                <Feather name="x" size={60} color={theme.colors.primaryActionText} />
              </Box>

              <Text variant="hero" textAlign="center" marginBottom="s" color="error">
                Verification Failed
              </Text>
              <Text variant="body" textAlign="center" marginBottom="l" color="secondaryText">
                We were unable to verify your identity. Please review the details below and try again.
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 300 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="title2" marginBottom="m" color="error">
                Verification Log
              </Text>

              {failedVerificationSteps.map((step, index) => (
                <VerificationLog key={index} message={step.message} status={step.status} index={index} />
              ))}
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 500 }}
          >
            <Box backgroundColor="errorLight" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center" marginBottom="s">
                <Feather name="alert-triangle" size={20} color={theme.colors.error} />
                <Text variant="body" fontWeight="600" color="error" marginLeft="s">
                  Common Issues
                </Text>
              </Box>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • ID card image is blurry or poorly lit
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Selfie doesn't clearly show your face
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Information entered doesn't match ID card
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Document may be damaged or expired
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 40 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 700 }}
          >
            <Box gap="m">
              <Button 
                label="Retry Verification" 
                onPress={handleRetry} 
              />
              <Button 
                label="Contact Support" 
                onPress={handleContactSupport} 
                variant="outline"
              />
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
} 