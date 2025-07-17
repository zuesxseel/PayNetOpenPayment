"use client"
import { useState } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, TextInput, ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function ConfirmDetailsScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  const { registrationData } = route.params
  const { icData } = registrationData

  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [pin, setPin] = useState("")
  const [confirmPin, setConfirmPin] = useState("")
  const [agreeTerms, setAgreeTerms] = useState(false)

  const handleSubmit = () => {
    if (!email || !phone || !pin || !confirmPin) {
      alert("Please fill in all required fields")
      return
    }

    if (pin.length !== 6) {
      alert("PIN must be exactly 6 digits")
      return
    }

    if (pin !== confirmPin) {
      alert("PINs do not match")
      return
    }

    if (!agreeTerms) {
      alert("Please agree to the terms and conditions")
      return
    }

    const completeRegistrationData = {
      ...registrationData,
      contactInfo: {
        email,
        phone,
        pin,
      },
    }

    navigation.navigate("AIVerification", { registrationData: completeRegistrationData })
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Confirm Details
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: 24 }}>
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Text variant="title2" textAlign="center" marginBottom="m">
              Step 3 of 3: Account Setup
            </Text>
            <Text variant="body" textAlign="center" marginBottom="l" color="secondaryText">
              Review your information and complete your account setup
            </Text>
          </MotiView>

          {/* IC Data Review */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center" marginBottom="m">
                <Feather name="credit-card" size={20} color={theme.colors.success} />
                <Text variant="body" fontWeight="600" color="success" marginLeft="s">
                  Identity Card Information
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  Full Name
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {icData.name}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  NRIC
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {icData.nric}
                </Text>
              </Box>

              <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                <Text variant="body" color="secondaryText">
                  Date of Birth
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText">
                  {icData.dateOfBirth}
                </Text>
              </Box>

              <Box marginTop="s">
                <Text variant="body" color="secondaryText" marginBottom="xs">
                  Address
                </Text>
                <Text variant="body" fontWeight="600" color="primaryText" fontSize={14}>
                  {icData.address}
                </Text>
              </Box>
            </Box>
          </MotiView>

          {/* Contact Information */}
          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
              <Text variant="body" fontWeight="600" color="primaryText" marginBottom="m">
                Contact Information
              </Text>

              <Box marginBottom="m">
                <Text variant="body" color="secondaryText" marginBottom="s">
                  Email Address *
                </Text>
                <Box
                  flexDirection="row"
                  alignItems="center"
                  backgroundColor="mainBackground"
                  borderRadius="m"
                  paddingHorizontal="m"
                  borderWidth={1}
                  borderColor="cardBorder"
                >
                  <Feather name="mail" size={20} color={theme.colors.secondaryText} />
                  <TextInput
                    value={email}
                    onChangeText={setEmail}
                    placeholder="your.email@example.com"
                    keyboardType="email-address"
                    style={{ flex: 1, height: 50, marginLeft: 12, fontSize: 16 }}
                  />
                </Box>
              </Box>

              <Box marginBottom="m">
                <Text variant="body" color="secondaryText" marginBottom="s">
                  Phone Number *
                </Text>
                <Box
                  flexDirection="row"
                  alignItems="center"
                  backgroundColor="mainBackground"
                  borderRadius="m"
                  paddingHorizontal="m"
                  borderWidth={1}
                  borderColor="cardBorder"
                >
                  <Feather name="phone" size={20} color={theme.colors.secondaryText} />
                  <TextInput
                    value={phone}
                    onChangeText={setPhone}
                    placeholder="+60 12-345 6789"
                    keyboardType="phone-pad"
                    style={{ flex: 1, height: 50, marginLeft: 12, fontSize: 16 }}
                  />
                </Box>
              </Box>

              <Box marginBottom="m">
                <Text variant="body" color="secondaryText" marginBottom="s">
                  Create PIN *
                </Text>
                <Box
                  flexDirection="row"
                  alignItems="center"
                  backgroundColor="mainBackground"
                  borderRadius="m"
                  paddingHorizontal="m"
                  borderWidth={1}
                  borderColor="cardBorder"
                >
                  <Feather name="lock" size={20} color={theme.colors.secondaryText} />
                  <TextInput
                    value={pin}
                    onChangeText={setPin}
                    placeholder="Enter 6-digit PIN"
                    keyboardType="numeric"
                    maxLength={6}
                    secureTextEntry
                    style={{ flex: 1, height: 50, marginLeft: 12, fontSize: 16 }}
                  />
                </Box>
              </Box>

              <Box>
                <Text variant="body" color="secondaryText" marginBottom="s">
                  Confirm PIN *
                </Text>
                <Box
                  flexDirection="row"
                  alignItems="center"
                  backgroundColor="mainBackground"
                  borderRadius="m"
                  paddingHorizontal="m"
                  borderWidth={1}
                  borderColor="cardBorder"
                >
                  <Feather name="lock" size={20} color={theme.colors.secondaryText} />
                  <TextInput
                    value={confirmPin}
                    onChangeText={setConfirmPin}
                    placeholder="Confirm your 6-digit PIN"
                    keyboardType="numeric"
                    maxLength={6}
                    secureTextEntry
                    style={{ flex: 1, height: 50, marginLeft: 12, fontSize: 16 }}
                  />
                </Box>
              </Box>
            </Box>
          </MotiView>

          {/* Terms Agreement */}
          <MotiView
            from={{ opacity: 0, translateY: 40 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <TouchableOpacity onPress={() => setAgreeTerms(!agreeTerms)}>
              <Box flexDirection="row" alignItems="center" marginBottom="l">
                <Box
                  width={24}
                  height={24}
                  borderRadius="s"
                  backgroundColor={agreeTerms ? "primaryAction" : "cardPrimaryBackground"}
                  borderWidth={2}
                  borderColor={agreeTerms ? "primaryAction" : "cardBorder"}
                  justifyContent="center"
                  alignItems="center"
                >
                  {agreeTerms && <Feather name="check" size={16} color={theme.colors.primaryActionText} />}
                </Box>
                <Text variant="body" fontSize={14} color="secondaryText" marginLeft="m" flex={1}>
                  I agree to the Terms of Service and Privacy Policy. I consent to the processing of my personal data
                  for identity verification purposes.
                </Text>
              </Box>
            </TouchableOpacity>
          </MotiView>

          <MotiView
            from={{ opacity: 0, translateY: 50 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="center">
                <Feather name="shield" size={20} color={theme.colors.primaryAction} />
                <Text variant="body" fontSize={14} color="primaryAction" marginLeft="s" fontWeight="600">
                  Your data is protected
                </Text>
              </Box>
              <Text variant="body" fontSize={12} color="secondaryText" marginTop="xs">
                We use bank-level encryption and comply with Malaysian data protection laws
              </Text>
            </Box>
          </MotiView>
        </ScrollView>

        <MotiView
          from={{ translateY: 50, opacity: 0 }}
          animate={{ translateY: 0, opacity: 1 }}
          transition={{ type: "timing", delay: 1000 }}
        >
          <Box padding="l">
            <Button label="Submit & Verify Identity" onPress={handleSubmit} disabled={!agreeTerms} />
          </Box>
        </MotiView>
      </SafeAreaView>
    </Box>
  )
}
