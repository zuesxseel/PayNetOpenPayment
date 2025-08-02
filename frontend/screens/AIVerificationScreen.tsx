"use client"
import { useState, useEffect } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const VerificationLog = ({ message, status, index }: { message: string; status: string; index: number }) => {
  const theme = useTheme()
  const getStatusIcon = () => {
    switch (status) {
      case "processing":
        return "loader"
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
      case "processing":
        return theme.colors.primaryAction
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
        <MotiView
          from={{ rotate: status === "processing" ? "0deg" : "0deg" }}
          animate={{ rotate: status === "processing" ? "360deg" : "0deg" }}
          transition={{ type: "timing", duration: 1000, loop: status === "processing" }}
        >
          <Feather name={getStatusIcon()} size={16} color={getStatusColor()} />
        </MotiView>
        <Text variant="body" fontSize={14} color="primaryText" marginLeft="m" flex={1}>
          {message}
        </Text>
      </Box>
    </MotiView>
  )
}

export default function AIVerificationScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  const { registrationData, verificationAttempt: routeAttempt } = route.params
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [verificationAttempt, setVerificationAttempt] = useState(routeAttempt || 1) // Use route param or default to 1

  // Success verification steps (all ticks)
  const successVerificationSteps = [
    { message: "Initializing verification engine...", status: "processing" },
    { message: "ID image received. Extracting text from ID...", status: "pending" },
    {
      message: `Extracted Name: ${registrationData.icData.name}, NRIC: ${registrationData.icData.nric}`,
      status: "pending",
    },
    { message: "Verifying ID card authenticity (hologram, layout, etc.)...", status: "pending" },
    { message: "ID document validity check passed.", status: "pending" },
    { message: "Performing facial recognition match...", status: "pending" },
    { message: "Comparing live selfie to ID photo...", status: "pending" },
    { message: "Face match successful (98% confidence).", status: "pending" },
    { message: "Conducting liveness check on selfie...", status: "pending" },
    { message: "Liveness check passed – user is physically present.", status: "pending" },
    { message: "Connecting to related identity database...", status: "pending" },
    { message: "Cross-checking NRIC and personal details with related records...", status: "pending" },
    { message: "Personal details verified with official records.", status: "pending" },
    { message: "All verification checks passed!", status: "pending" },
    { message: "Account creation in progress...", status: "pending" },
  ]

  // Failure verification steps (mostly crosses)
  const failureVerificationSteps = [
    { message: "Initializing verification engine...", status: "processing" as const },
    { message: "ID image received. Extracting text from ID...", status: "pending" as const },
    {
      message: `Extracted Name: ${registrationData.icData.name}, NRIC: ${registrationData.icData.nric}`,
      status: "pending" as const,
    },
    { message: "Verifying ID card authenticity (hologram, layout, etc.)...", status: "pending" as const, willFail: true },
    { message: "ID document validity check failed - suspicious patterns detected.", status: "pending" as const, willFail: true },
    { message: "Performing facial recognition match...", status: "pending" as const, willFail: true },
    { message: "Comparing live selfie to ID photo...", status: "pending" as const, willFail: true },
    { message: "Face match failed (42% confidence) - insufficient similarity.", status: "pending" as const, willFail: true },
    { message: "Conducting liveness check on selfie...", status: "pending" as const, willFail: true },
    { message: "Liveness check failed - potential spoofing detected.", status: "pending" as const, willFail: true },
    { message: "Connecting to related identity database...", status: "pending" as const },
    { message: "Cross-checking NRIC and personal details with related records...", status: "pending" as const, willFail: true },
    { message: "Personal details mismatch with official records.", status: "pending" as const, willFail: true },
    { message: "Verification failed - multiple checks did not pass.", status: "pending" as const, willFail: true },
  ]

  // Determine if this is success or failure attempt
  const isSuccessAttempt = verificationAttempt === 1
  const verificationSteps = isSuccessAttempt ? successVerificationSteps : failureVerificationSteps

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < verificationSteps.length - 1) {
          const newStep = prev + 1
          setProgress((newStep / verificationSteps.length) * 100)
          return newStep
        } else {
          setIsComplete(true)
          clearInterval(interval)
          // Navigate based on attempt number
          setTimeout(() => {
            if (isSuccessAttempt) {
              navigation.navigate("VerificationSuccess", { registrationData })
            } else {
              navigation.navigate("VerificationFailed", { registrationData })
            }
          }, 2000)
          return prev
        }
      })
    }, 1500) // Each step takes 1.5 seconds

    return () => clearInterval(interval)
  }, [verificationAttempt])

  const getStepStatus = (index: number) => {
    if (index < currentStep) {
      // For failure attempt, show error for steps marked as willFail
      if (!isSuccessAttempt && (verificationSteps[index] as any)?.willFail) {
        return "error"
      }
      return "success"
    }
    if (index === currentStep) return "processing"
    return "pending"
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box padding="l" backgroundColor="cardPrimaryBackground">
          <Box alignItems="center">
            <MotiView from={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "timing", duration: 500 }}>
              <Box
                width={80}
                height={80}
                backgroundColor="primaryAction"
                borderRadius="xl"
                justifyContent="center"
                alignItems="center"
                marginBottom="m"
              >
                <MotiView
                  from={{ rotate: "0deg" }}
                  animate={{ rotate: "360deg" }}
                  transition={{ type: "timing", duration: 2000, loop: !isComplete }}
                >
                  <Feather name="cpu" size={40} color={theme.colors.primaryActionText} />
                </MotiView>
              </Box>
            </MotiView>

            <Text variant="title1" textAlign="center" marginBottom="s">
              Verifying Documents
            </Text>
            <Text variant="body" textAlign="center" color="secondaryText" marginBottom="m">
              We are verifying your identity and documents
            </Text>

            {/* Progress Bar */}
            <Box width="100%" height={8} backgroundColor="cardBorder" borderRadius="s" marginBottom="s">
              <MotiView
                from={{ width: "0%" }}
                animate={{ width: `${progress}%` }}
                transition={{ type: "timing", duration: 300 }}
              >
                <Box height="100%" backgroundColor="primaryAction" borderRadius="s" />
              </MotiView>
            </Box>

            <Text variant="body" fontSize={14} color="secondaryText">
              Progress: {Math.round(progress)}% • Usually takes 10-15 minutes
            </Text>
          </Box>
        </Box>

        <ScrollView contentContainerStyle={{ padding: 24 }}>
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="title2" marginBottom="m">
                Verification Status
              </Text>

              {verificationSteps.slice(0, currentStep + 1).map((step, index) => (
                <VerificationLog key={index} message={step.message} status={getStepStatus(index)} index={index} />
              ))}
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="blueLight" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center" marginBottom="s">
                <Feather name="info" size={20} color={theme.colors.primaryAction} />
                <Text variant="body" fontWeight="600" color="primaryAction" marginLeft="s">
                  What's happening?
                </Text>
              </Box>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Extracting data from your IC using OCR technology
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Comparing your selfie with the photo on your IC
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" marginBottom="s">
                • Verifying document authenticity and security features
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText">
                • Cross-checking with related databases
              </Text>
            </Box>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 40 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Box backgroundColor="warning" padding="m" borderRadius="m">
              <Text variant="body" fontSize={12} color="primaryActionText" textAlign="center">
                ⏱️ Please keep the app open. You'll be notified once verification is complete.
              </Text>
            </Box>
          </MotiView>
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}