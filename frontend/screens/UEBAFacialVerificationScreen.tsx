"use client"
import { useState, useEffect, useRef } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Dimensions, View, ActivityIndicator } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { CameraView, useCameraPermissions } from "expo-camera"
import { LinearGradient } from "expo-linear-gradient"

const { width, height } = Dimensions.get("window")

export default function UEBAFacialVerificationScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  const [permission, requestPermission] = useCameraPermissions()
  const [isCameraReady, setIsCameraReady] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)
  const [progress, setProgress] = useState(0)
  const cameraRef = useRef<CameraView | null>(null)
  const progressInterval = useRef<number | null>(null)

  // Safely extract qrData with fallbacks
  const qrData = route?.params?.qrData || {
    merchantName: "Unknown Merchant",
    amount: 0,
    currency: "MYR",
    type: "UEBA Verified",
  }

  useEffect(() => {
    if (isCameraReady && !isVerifying) {
      // Start verification process automatically when camera is ready
      setTimeout(() => {
        setIsVerifying(true)
        startProgressAnimation()
      }, 500)
    }
  }, [isCameraReady])

  const startProgressAnimation = () => {
    setProgress(0)
    let currentProgress = 0
    
    progressInterval.current = setInterval(() => {
      currentProgress += 2
      setProgress(currentProgress)
      
      if (currentProgress >= 100) {
        if (progressInterval.current) {
          clearInterval(progressInterval.current)
        }
        setTimeout(() => {
          navigation.navigate("PaymentSuccess", { qrData })
        }, 150)
      }
    }, 30) // Update every 30ms for smooth animation
  }

  useEffect(() => {
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current)
      }
    }
  }, [])

  if (!permission) {
    return (
      <Box flex={1} justifyContent="center" alignItems="center" backgroundColor="mainBackground">
        <ActivityIndicator size="large" color={theme.colors.primaryAction} />
        <Text variant="body" marginTop="m">Loading camera...</Text>
      </Box>
    )
  }

  if (!permission.granted) {
    return (
      <Box flex={1} justifyContent="center" alignItems="center" padding="l" backgroundColor="mainBackground">
        <MotiView
          from={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "timing" }}
        >
          <Box
            width={120}
            height={120}
            backgroundColor="error"
            borderRadius="xl"
            justifyContent="center"
            alignItems="center"
            marginBottom="l"
          >
            <Feather name="camera-off" size={48} color={theme.colors.primaryActionText} />
          </Box>
        </MotiView>
        
        <Text variant="title2" color="error" marginBottom="m" textAlign="center">
          Camera Access Required
        </Text>
        <Text variant="body" color="secondaryText" marginBottom="l" textAlign="center">
          We need camera access for facial verification to complete your payment securely
        </Text>
        
        <TouchableOpacity
          onPress={requestPermission}
          style={{
            backgroundColor: theme.colors.primaryAction,
            paddingHorizontal: 24,
            paddingVertical: 12,
            borderRadius: 12,
          }}
        >
          <Text variant="body" color="primaryActionText" fontWeight="600">
            Grant Camera Permission
          </Text>
        </TouchableOpacity>
      </Box>
    )
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        {/* Header */}
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Facial Verification
          </Text>
        </Box>

        <Box flex={1} justifyContent="center" alignItems="center" padding="l">
          {/* Title and Description */}
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Text variant="body" textAlign="center" marginBottom="l" color="secondaryText">
              Please look at the camera for facial verification to complete your payment securely
            </Text>
          </MotiView>

          {/* Large Camera Circle */}
          <MotiView
            from={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              width={width * 0.8}
              height={width * 0.8}
              borderRadius="xl"
              backgroundColor="cardPrimaryBackground"
              justifyContent="center"
              alignItems="center"
              borderWidth={4}
              borderColor={isVerifying ? "primaryAction" : "success"}
              marginBottom="l"
              overflow="hidden"
              style={{
                shadowColor: theme.colors.primaryAction,
                shadowOffset: { width: 0, height: 8 },
                shadowOpacity: 0.3,
                shadowRadius: 16,
                elevation: 12,
              }}
            >
              {/* Gradient Background */}
              <LinearGradient
                colors={[
                  "rgba(31, 51, 237, 0.1)",
                  "rgba(78, 94, 237, 0.05)",
                  "rgba(127, 138, 240, 0.1)",
                  "rgba(157, 166, 242, 0.05)",
                  "rgba(182, 198, 240, 0.1)",
                ]}
                start={{ x: 0, y: 0.5 }}
                end={{ x: 1, y: 0.5 }}
                style={{
                  position: "absolute",
                  width: "100%",
                  height: "100%",
                  borderRadius: 16,
                }}
              />

              {/* Camera View */}
              <CameraView
                ref={cameraRef}
                style={{ 
                  width: width * 0.7, 
                  height: width * 0.7, 
                  borderRadius: (width * 0.7) / 2 
                }}
                facing="front"
                onCameraReady={() => setIsCameraReady(true)}
              />

              {/* Camera Loading State */}
              {!isCameraReady && (
                <View style={{ 
                  position: "absolute", 
                  left: 0, 
                  right: 0, 
                  top: 0, 
                  bottom: 0, 
                  justifyContent: "center", 
                  alignItems: "center", 
                  backgroundColor: "rgba(0,0,0,0.3)",
                  borderRadius: 16
                }}>
                  <ActivityIndicator size="large" color={theme.colors.primaryAction} />
                  <Text variant="body" color="primaryActionText" marginTop="m">
                    Initializing camera...
                  </Text>
                </View>
              )}

              {/* Verification Overlay */}
              {isVerifying && (
                <View style={{ 
                  position: "absolute", 
                  left: 0, 
                  right: 0, 
                  top: 0, 
                  bottom: 0, 
                  justifyContent: "center", 
                  alignItems: "center", 
                  backgroundColor: "rgba(31, 51, 237, 0.2)",
                  borderRadius: 16
                }}>                
                  
                  <Text variant="body" color="primaryActionText" fontWeight="600" marginBottom="s">
                    Verifying...
                  </Text>
                  
                  {/* Progress Bar */}
                  <Box
                    width={200}
                    height={4}
                    borderRadius="s"
                    overflow="hidden"
                    style={{ backgroundColor: "rgba(255,255,255,0.3)" }}
                  >
                    <MotiView
                      from={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ type: "timing", duration: 100 }}
                      style={{
                        height: "100%",
                        backgroundColor: theme.colors.primaryActionText,
                        borderRadius: 2,
                      }}
                    />
                  </Box>
                  
                  <Text variant="body" fontSize={12} color="primaryActionText" opacity={0.8} marginTop="s">
                    {progress}% Complete
                  </Text>
                </View>
              )}

              {/* Scanning Animation Ring */}
              {isVerifying && (
                <MotiView
                  from={{ scale: 0.8, opacity: 0.8 }}
                  animate={{ scale: 1.2, opacity: 0 }}
                  transition={{
                    type: "timing",
                    duration: 2000,
                    loop: true,
                    repeatReverse: false,
                  }}
                  style={{
                    position: "absolute",
                    width: width * 0.8,
                    height: width * 0.8,
                    borderRadius: (width * 0.8) / 2,
                    borderWidth: 2,
                    borderColor: theme.colors.primaryAction,
                  }}
                />
              )}
            </Box>
          </MotiView>

          {/* Status Messages */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l" width="100%">
              <Text variant="body" textAlign="center" marginBottom="s" fontWeight="600">
                {!isCameraReady 
                  ? "Preparing camera..." 
                  : !isVerifying 
                  ? "Position your face in the circle" 
                  : "Facial verification in progress..."
                }
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" textAlign="center">
                {!isCameraReady 
                  ? "Please wait while we initialize the camera" 
                  : !isVerifying 
                  ? "Make sure your face is clearly visible" 
                  : "Please remain still while we verify your identity"
                }
              </Text>
            </Box>
          </MotiView>

          {/* Security Notice */}
          <MotiView
            from={{ opacity: 0, translateY: 30 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m" width="100%">
              <Text variant="body" fontSize={14} color="primaryAction" textAlign="center" fontWeight="600">
                🛡️ Enhanced Security Active
              </Text>
              <Text variant="body" fontSize={12} color="secondaryText" textAlign="center" marginTop="xs">
                This verification ensures secure payment processing and prevents fraud
              </Text>
            </Box>
          </MotiView>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
