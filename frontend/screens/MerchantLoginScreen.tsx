"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { TextInput, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { useAuth } from "../context/AuthContext"
import { MotiView } from "moti"

export default function MerchantLoginScreen({ navigation }) {
  const theme = useTheme()
  const { login } = useAuth()

  const handleMerchantLogin = () => {
    login("merchant")
  }

  return (
    <Box flex={1} backgroundColor="mainBackground" padding="l">
      <SafeAreaView style={{ flex: 1 }}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
        </TouchableOpacity>
        <Box flex={1} justifyContent="center">
          <MotiView
            from={{ translateY: -20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing" }}
          >
            <Text variant="title1" marginBottom="s">
              Merchant Portal
            </Text>
            <Text variant="body">Access your business dashboard and payment analytics.</Text>
          </MotiView>

          <MotiView
            from={{ translateY: 20, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              flexDirection="row"
              alignItems="center"
              backgroundColor="cardPrimaryBackground"
              borderRadius="m"
              paddingHorizontal="m"
              marginTop="xl"
              borderWidth={1}
              borderColor="cardBorder"
            >
              <Feather name="mail" size={20} color={theme.colors.secondaryText} />
              <TextInput
                placeholder="Business Email"
                style={{ flex: 1, height: 56, marginLeft: theme.spacing.m, fontSize: 16 }}
                keyboardType="email-address"
              />
            </Box>
            <Box
              flexDirection="row"
              alignItems="center"
              backgroundColor="cardPrimaryBackground"
              borderRadius="m"
              paddingHorizontal="m"
              marginTop="m"
              borderWidth={1}
              borderColor="cardBorder"
            >
              <Feather name="lock" size={20} color={theme.colors.secondaryText} />
              <TextInput
                placeholder="Password"
                secureTextEntry
                style={{ flex: 1, height: 56, marginLeft: theme.spacing.m, fontSize: 16 }}
              />
            </Box>
          </MotiView>
        </Box>
        <MotiView
          from={{ translateY: 50, opacity: 0 }}
          animate={{ translateY: 0, opacity: 1 }}
          transition={{ type: "timing", delay: 400 }}
        >
          <Button label="Access Merchant Dashboard" onPress={handleMerchantLogin} />
          <Button
            label="Scan Terminal QR"
            onPress={() => {
              /* Handle QR Terminal Scan */
            }}
            variant="outline"
            marginTop="m"
          />
        </MotiView>
      </SafeAreaView>
    </Box>
  )
}
