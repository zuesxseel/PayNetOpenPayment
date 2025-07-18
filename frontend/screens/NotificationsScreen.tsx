import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

interface NotificationItemProps {
  icon: string;
  title: string;
  message: string;
  time: string;
  type: string;
  index: number;
  onPress: () => void;
}

const NotificationItem = ({ icon, title, message, time, type, index, onPress }: NotificationItemProps) => {
  const theme = useTheme()

  const getIconColor = () => {
    switch (type) {
      case "zkp":
        return "#FF6B6B"
      case "ueba":
        return "#FFA726"
      case "success":
        return "#4CAF50"
      default:
        return theme.colors.primaryAction
    }
  }

  const getBackgroundColor = () => {
    switch (type) {
      case "zkp":
        return "rgba(255, 107, 107, 0.1)"
      case "ueba":
        return "rgba(255, 167, 38, 0.1)"
      case "success":
        return "rgba(76, 175, 80, 0.1)"
      default:
        return theme.colors.cardPrimaryBackground
    }
  }

  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <TouchableOpacity onPress={onPress}>
        <Box
          backgroundColor="cardPrimaryBackground"
          borderRadius="l"
          padding="m"
          marginBottom="s"
          flexDirection="row"
          alignItems="flex-start"
          style={{ backgroundColor: getBackgroundColor() }}
        >
          <Box
            width={40}
            height={40}
            borderRadius="xl"
            justifyContent="center"
            alignItems="center"
            style={{ backgroundColor: getIconColor() + "20" }}
          >
            <Feather name={icon as any} size={20} color={getIconColor()} />
          </Box>
          <Box flex={1} marginLeft="m">
            <Text variant="body" fontWeight="600" color="primaryText" marginBottom="xs">
              {title}
            </Text>
            <Text variant="body" fontSize={14} color="secondaryText" marginBottom="xs">
              {message}
            </Text>
            <Text variant="body" fontSize={12} color="secondaryText">
              {time}
            </Text>
          </Box>
          <Feather name="chevron-right" size={16} color={theme.colors.secondaryText} />
        </Box>
      </TouchableOpacity>
    </MotiView>
  )
}

interface NotificationsScreenProps {
  navigation: any;
}

export default function NotificationsScreen({ navigation }: NotificationsScreenProps) {
  const theme = useTheme()

  const notifications = [
    {
      id: 1,
      icon: "shield-off",
      title: "ZKP Verification Failed",
      message: "Your recent transaction requires additional verification. Please complete the pattern verification.",
      time: "2 minutes ago",
      type: "zkp",
      action: () => navigation.navigate("ZKPBlocked"),
    },
    {
      id: 2,
      icon: "alert-triangle",
      title: "Suspicious Activity Detected",
      message: "Login attempt from foreign location detected. Please verify your identity.",
      time: "5 minutes ago",
      type: "ueba",
      action: () => navigation.navigate("UEBAVerification"),
    },
    {
      id: 3,
      icon: "check-circle",
      title: "Payment Successful",
      message: "Your payment to FamilyMart has been processed successfully.",
      time: "1 hour ago",
      type: "success",
      action: () => {},
    },
    {
      id: 4,
      icon: "info",
      title: "Security Update",
      message: "New security features have been added to protect your account.",
      time: "2 hours ago",
      type: "info",
      action: () => {},
    },
  ]

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView>
        <Box flexDirection="row" alignItems="center" justifyContent="space-between" padding="l">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title2" color="primaryText">
            Notifications
          </Text>
          <TouchableOpacity>
            <Feather name="settings" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
        </Box>

        <ScrollView showsVerticalScrollIndicator={false} style={{ paddingHorizontal: theme.spacing.l }}>
          <Text variant="body" color="secondaryText" marginBottom="m">
            Recent notifications and security alerts
          </Text>

          {notifications.map((notification, index) => (
            <NotificationItem
              key={notification.id}
              icon={notification.icon}
              title={notification.title}
              message={notification.message}
              time={notification.time}
              type={notification.type}
              index={index}
              onPress={notification.action}
            />
          ))}
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
