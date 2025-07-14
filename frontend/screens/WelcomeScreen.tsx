"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

export default function WelcomeScreen({ navigation }) {
  const theme = useTheme()

  return (
    <Box flex={1} backgroundColor="cardPrimaryBackground" justifyContent="center" padding="l">
      <SafeAreaView>
        <Box alignItems="center" marginBottom="xl">
          <MotiView
            from={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", duration: 500 }}
          >
            <Box
              width={80}
              height={80}
              backgroundColor="primaryAction"
              borderRadius="xl"
              justifyContent="center"
              alignItems="center"
            >
              <Feather name="globe" size={40} color={theme.colors.primaryActionText} />
            </Box>
          </MotiView>
          <Text variant="hero" textAlign="center" marginTop="l">
            Open Payment
          </Text>
          <Text variant="body" textAlign="center" marginTop="m">
            The borderless wallet for everyone. Simple, secure, and always on.
          </Text>
        </Box>
        <MotiView
          from={{ translateY: 50, opacity: 0 }}
          animate={{ translateY: 0, opacity: 1 }}
          transition={{ type: "timing", duration: 500, delay: 200 }}
        >
          <Button label="Login as User" onPress={() => navigation.navigate("UserLogin")} />
          <Button
            label="Merchant Portal"
            onPress={() => navigation.navigate("MerchantLogin")}
            variant="outline"
            marginTop="m"
          />
        </MotiView>
      </SafeAreaView>
    </Box>
  )
}
