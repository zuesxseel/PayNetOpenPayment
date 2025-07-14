"use client"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Image } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { useAuth } from "../context/AuthContext"
import { MotiView } from "moti"

const ProfileMenuItem = ({ icon, label, onPress, index }) => {
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
          padding="m"
          borderRadius="m"
        >
          <Box
            width={40}
            height={40}
            backgroundColor="blueLight"
            borderRadius="l"
            justifyContent="center"
            alignItems="center"
          >
            <Feather name={icon} size={20} color={theme.colors.primaryAction} />
          </Box>
          <Text variant="body" flex={1} marginLeft="m" color="primaryText">
            {label}
          </Text>
          <Feather name="chevron-right" size={20} color={theme.colors.secondaryText} />
        </Box>
      </TouchableOpacity>
    </MotiView>
  )
}

export default function ProfileScreen() {
  const { logout, userType } = useAuth()

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <MotiView
          from={{ opacity: 0, translateY: -20 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: "timing" }}
        >
          <Box alignItems="center" padding="xl" backgroundColor="cardPrimaryBackground">
            <Image
              source={{ uri: "https://i.pravatar.cc/150?u=a042581f4e29026704d" }}
              style={{ width: 100, height: 100, borderRadius: 50, marginBottom: 16 }}
            />
            <Text variant="title2">{userType === "merchant" ? "Business Account" : "Alex Lim"}</Text>
            <Text variant="body">{userType === "merchant" ? "Merchant ID: M123456" : "@alexlim99"}</Text>
          </Box>
        </MotiView>

        <Box flex={1} padding="l" gap="m">
          <ProfileMenuItem icon="user" label="Account Details" onPress={() => {}} index={0} />
          <ProfileMenuItem icon="shield" label="Security & Privacy" onPress={() => {}} index={1} />
          <ProfileMenuItem icon="bell" label="Notifications" onPress={() => {}} index={2} />
          <ProfileMenuItem icon="help-circle" label="Help & Support" onPress={() => {}} index={3} />
          {userType === "merchant" && (
            <ProfileMenuItem icon="bar-chart" label="Business Analytics" onPress={() => {}} index={4} />
          )}
        </Box>

        <MotiView
          from={{ translateY: 50, opacity: 0 }}
          animate={{ translateY: 0, opacity: 1 }}
          transition={{ type: "timing", delay: 500 }}
        >
          <Box padding="l">
            <Button label="Log Out" onPress={logout} variant="outline" />
          </Box>
        </MotiView>
      </SafeAreaView>
    </Box>
  )
}
