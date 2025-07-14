"use client"
import { useState } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { ScrollView, TouchableOpacity, Switch } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"

const SettingItem = ({ icon, label, value, onPress, hasSwitch = false, switchValue, onSwitchChange, index }) => {
  const theme = useTheme()
  return (
    <MotiView
      from={{ opacity: 0, translateX: -20 }}
      animate={{ opacity: 1, translateX: 0 }}
      transition={{ type: "timing", delay: 100 * index }}
    >
      <TouchableOpacity onPress={onPress} disabled={hasSwitch}>
        <Box
          flexDirection="row"
          alignItems="center"
          backgroundColor="cardPrimaryBackground"
          padding="l"
          borderRadius="m"
          marginBottom="s"
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
          <Box flex={1} marginLeft="m">
            <Text variant="body" color="primaryText" fontWeight="600">
              {label}
            </Text>
            {value && (
              <Text variant="body" fontSize={14} color="secondaryText" marginTop="xs">
                {value}
              </Text>
            )}
          </Box>
          {hasSwitch ? (
            <Switch
              trackColor={{ false: theme.colors.cardBorder, true: theme.colors.primaryAction }}
              thumbColor={switchValue ? theme.colors.primaryActionText : theme.colors.cardPrimaryBackground}
              onValueChange={onSwitchChange}
              value={switchValue}
            />
          ) : (
            <Feather name="chevron-right" size={20} color={theme.colors.secondaryText} />
          )}
        </Box>
      </TouchableOpacity>
    </MotiView>
  )
}

export default function MerchantSettingsScreen({ navigation }) {
  const theme = useTheme()
  const [qrFallback, setQrFallback] = useState(true)
  const [faceRecognition, setFaceRecognition] = useState(true)
  const [autoReceipt, setAutoReceipt] = useState(false)

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Merchant Settings
          </Text>
        </Box>

        <ScrollView contentContainerStyle={{ padding: 24 }}>
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Text variant="title2" marginBottom="m">
              Payment Settings
            </Text>
          </MotiView>

          <SettingItem
            icon="dollar-sign"
            label="Default Currency"
            value="Malaysian Ringgit (MYR)"
            onPress={() => {}}
            index={0}
          />

          <SettingItem
            icon="credit-card"
            label="Preferred Wallet Types"
            value="GrabPay, Boost, TNG eWallet"
            onPress={() => {}}
            index={1}
          />

          <SettingItem
            icon="grid"
            label="QR Code Fallback"
            hasSwitch={true}
            switchValue={qrFallback}
            onSwitchChange={setQrFallback}
            index={2}
          />

          <SettingItem
            icon="user-check"
            label="Face Recognition"
            hasSwitch={true}
            switchValue={faceRecognition}
            onSwitchChange={setFaceRecognition}
            index={3}
          />

          <MotiView
            from={{ opacity: 0, translateY: -10 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 500 }}
          >
            <Text variant="title2" marginTop="l" marginBottom="m">
              Security & Compliance
            </Text>
          </MotiView>

          <SettingItem icon="shield" label="Risk Threshold" value="Medium (25%)" onPress={() => {}} index={4} />

          <SettingItem icon="lock" label="PIN Attempts Limit" value="3 attempts" onPress={() => {}} index={5} />

          <SettingItem
            icon="eye"
            label="Fraud Detection"
            value="AI-powered monitoring enabled"
            onPress={() => {}}
            index={6}
          />

          <MotiView
            from={{ opacity: 0, translateY: -10 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 700 }}
          >
            <Text variant="title2" marginTop="l" marginBottom="m">
              Receipt & Notifications
            </Text>
          </MotiView>

          <SettingItem
            icon="mail"
            label="Auto-send Receipts"
            hasSwitch={true}
            switchValue={autoReceipt}
            onSwitchChange={setAutoReceipt}
            index={7}
          />

          <SettingItem
            icon="bell"
            label="Transaction Alerts"
            value="Push notifications enabled"
            onPress={() => {}}
            index={8}
          />

          <SettingItem
            icon="printer"
            label="Receipt Template"
            value="Standard business format"
            onPress={() => {}}
            index={9}
          />
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
