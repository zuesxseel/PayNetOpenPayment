"use client"
import { useState, useEffect, useRef } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Dimensions, Image, View, ActivityIndicator } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { CameraView, useCameraPermissions } from "expo-camera"

const { width } = Dimensions.get("window")

export default function FacialVerificationScreen({ route, navigation }: { route: any; navigation: any }) {
  const theme = useTheme()
  
  // Handle icData with fallback to mock data if not provided
  const icData = route?.params?.icData || {
    name: "ALI BIN HASSAN",
    nric: "901234-56-7890",
    dateOfBirth: "12 JAN 1990",
    address: "NO 123, JALAN BUKIT BINTANG, 50200 KUALA LUMPUR",
    nationality: "WARGANEGARA",
    religion: "ISLAM",
    gender: "LELAKI",
  }
  
  const [permission, requestPermission] = useCameraPermissions()
  const [isCameraReady, setIsCameraReady] = useState(false)
  const [isCapturing, setIsCapturing] = useState(false)
  const [captureComplete, setCaptureComplete] = useState(false)
  const [captureFailed, setCaptureFailed] = useState(false)
  const [livenessStep, setLivenessStep] = useState(0)
  const [selfieData, setSelfieData] = useState<any>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [showLivenessDetection, setShowLivenessDetection] = useState(true)
  const [attemptCount, setAttemptCount] = useState(0)
  const cameraRef = useRef<CameraView | null>(null)

  const livenessSteps = [
    { instruction: "Look straight at the camera", icon: "eye" },
    { instruction: "Blink your eyes", icon: "eye-off" },
    { instruction: "Move your face slowly in a circle", icon: "rotate-cw" },
    { instruction: "Smile naturally", icon: "smile" },
  ]

  useEffect(() => {
    if (isCapturing && livenessStep < livenessSteps.length) {
      const timer = setTimeout(() => {
        setLivenessStep((prev) => prev + 1)
      }, 2000)
      return () => clearTimeout(timer)
    } else if (livenessStep >= livenessSteps.length && isCapturing) {
      // Complete liveness check and capture photo
      setTimeout(() => {
        handleCapturePhoto()
      }, 1000)
    }
  }, [livenessStep, isCapturing])

  const handleStartLivenessDetection = () => {
    setIsCapturing(true)
    setLivenessStep(0)
    setShowLivenessDetection(true)
  }

  const handleCapturePhoto = async () => {
    if (cameraRef.current && isCameraReady) {
      try {
        const photo = await cameraRef.current.takePictureAsync({ quality: 0.8, base64: false })
        setCapturedImage(photo.uri)
        setIsCapturing(false)
        
        // Increment attempt count
        const currentAttempt = attemptCount + 1
        setAttemptCount(currentAttempt)
        
        // Random verification result (70% success, 30% failure for better testing)
        const verificationSuccess = Math.random() > 0.3
        
        if (verificationSuccess) {
          setCaptureComplete(true)
          setShowLivenessDetection(false)
          setSelfieData({
            image: photo.uri,
            livenessScore: Math.floor(Math.random() * 10) + 90, // 90-99%
            quality: "High",
            verified: true
          })
        } else {
          // Navigate to failure screen
          setCaptureFailed(true)
          setSelfieData({
            image: photo.uri,
            livenessScore: Math.floor(Math.random() * 40) + 30, // 30-69%
            quality: Math.random() > 0.5 ? "Low" : "Medium",
            verified: false
          })
        }
      } catch (e) {
        console.log('Error taking selfie:', e)
      }
    }
  }

  const handleRetake = () => {
    setIsCapturing(false)
    setCaptureComplete(false)
    setCaptureFailed(false)
    setLivenessStep(0)
    setSelfieData(null)
    setCapturedImage(null)
    setShowLivenessDetection(true)
    // Don't reset attemptCount - preserve it across retakes
  }

  const handleConfirm = () => {
    const registrationData = {
      icData,
      selfieData,
      timestamp: new Date().toISOString(),
    }
    navigation.navigate("ConfirmDetails", { registrationData })
  }

  if (!permission) {
    return (
      <Box flex={1} justifyContent="center" alignItems="center">
        <ActivityIndicator size="large" color={theme.colors.primaryAction} />
        <Text variant="body" marginTop="m">Loading camera...</Text>
      </Box>
    )
  }

  if (!permission.granted) {
    return (
      <Box flex={1} justifyContent="center" alignItems="center" padding="l">
        <Feather name="camera-off" size={48} color={theme.colors.primaryAction} />
        <Text variant="body" color="primaryAction" marginTop="m" textAlign="center">
          We need camera access for facial verification
        </Text>
        <Button 
          label="Grant Camera Permission" 
          onPress={requestPermission} 
          marginTop="l"
        />
      </Box>
    )
  }

  if (captureComplete) {
    return (
      <Box flex={1} backgroundColor="mainBackground">
        <SafeAreaView style={{ flex: 1 }}>
          <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
            <TouchableOpacity onPress={() => navigation.goBack()}>
              <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
            </TouchableOpacity>
            <Text variant="title1" marginLeft="m">
              Selfie Captured
            </Text>
          </Box>

          <Box flex={1} justifyContent="center" alignItems="center" padding="l">
            <MotiView
              from={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "timing" }}
            >
              {capturedImage ? (
                <Image
                  source={{ uri: capturedImage }}
                  style={{ width: 200, height: 200, borderRadius: 100, marginBottom: 24 }}
                  resizeMode="cover"
                />
              ) : (
                <Box
                  width={200}
                  height={200}
                  backgroundColor="success"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                  marginBottom="l"
                >
                  <Feather name="user-check" size={80} color={theme.colors.primaryActionText} />
                </Box>
              )}
            </MotiView>

            <MotiView
              from={{ translateY: 20, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Text variant="title1" textAlign="center" marginBottom="s" color="success">
                Selfie Verified!
              </Text>
              <Text variant="body" textAlign="center" marginBottom="l" color="secondaryText">
                Your live selfie has been captured successfully
              </Text>
            </MotiView>

            <MotiView
              from={{ translateY: 30, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 400 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l" width="100%">
                <Text variant="title2" marginBottom="m" textAlign="center">
                  Verification Results
                </Text>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Liveness Score
                  </Text>
                  <Text variant="body" fontWeight="600" color="success">
                    {selfieData?.livenessScore}%
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Image Quality
                  </Text>
                  <Text variant="body" fontWeight="600" color="success">
                    {selfieData?.quality}
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    Liveness Check
                  </Text>
                  <Box flexDirection="row" alignItems="center">
                    <Feather name="check-circle" size={16} color={theme.colors.success} />
                    <Text variant="body" fontWeight="600" color="success" marginLeft="xs">
                      Passed
                    </Text>
                  </Box>
                </Box>
              </Box>
            </MotiView>

            <MotiView
              from={{ translateY: 40, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 600 }}
            >
              <Button label="Continue" onPress={handleConfirm} paddingHorizontal="l"/>
            </MotiView>
          </Box>
        </SafeAreaView>
      </Box>
    )
  }

  if (captureFailed) {
    return (
      <Box flex={1} backgroundColor="mainBackground">
        <SafeAreaView style={{ flex: 1 }}>
          <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
            <TouchableOpacity onPress={() => navigation.goBack()}>
              <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
            </TouchableOpacity>
            <Text variant="title1" marginLeft="m">
              Selfie Failed
            </Text>
          </Box>

          <Box flex={1} justifyContent="center" alignItems="center" padding="l">
            <MotiView
              from={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "timing" }}
            >
              {capturedImage ? (
                <Image
                  source={{ uri: capturedImage }}
                  style={{ width: 200, height: 200, borderRadius: 100, marginBottom: 24 }}
                  resizeMode="cover"
                />
              ) : (
                <Box
                  width={200}
                  height={200}
                  backgroundColor="error"
                  borderRadius="xl"
                  justifyContent="center"
                  alignItems="center"
                  marginBottom="l"
                >
                  <Feather name="user-x" size={80} color={theme.colors.primaryActionText} />
                </Box>
              )}
            </MotiView>

            <MotiView
              from={{ translateY: 20, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Text variant="title1" textAlign="center" marginBottom="s" color="error">
                Selfie Rejected
              </Text>
              <Text variant="body" textAlign="center" marginBottom="l" color="secondaryText">
                Your live selfie did not meet the required liveness standards.
              </Text>
            </MotiView>

            <MotiView
              from={{ translateY: 30, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 400 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l" width="100%">
                <Text variant="title2" marginBottom="m" textAlign="center">
                  Verification Results
                </Text>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Liveness Score
                  </Text>
                  <Text variant="body" fontWeight="600" color="error">
                    {selfieData?.livenessScore}%
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Image Quality
                  </Text>
                  <Text variant="body" fontWeight="600" color="error">
                    {selfieData?.quality}
                  </Text>
                </Box>

                <Box flexDirection="row" justifyContent="space-between">
                  <Text variant="body" color="secondaryText">
                    Liveness Check
                  </Text>
                  <Box flexDirection="row" alignItems="center">
                    <Feather name="x-circle" size={16} color={theme.colors.error} />
                    <Text variant="body" fontWeight="600" color="error" marginLeft="xs">
                      Failed
                    </Text>
                  </Box>
                </Box>
              </Box>
            </MotiView>

            <MotiView
              from={{ translateY: 40, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 600 }}
            >
              <Button label="Retake Selfie" onPress={handleRetake} paddingHorizontal="l"/>
            </MotiView>
          </Box>
        </SafeAreaView>
      </Box>
    )
  }

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title1" marginLeft="m">
            Facial Verification
          </Text>
        </Box>

        <Box flex={1} justifyContent="center" alignItems="center" padding="l">
          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing" }}
            style={{ marginTop: 20 }}
          >
            <Text variant="title2" textAlign="center" marginBottom="m">
              Step 2 of 3: Live Selfie
            </Text>
            <Text variant="body" textAlign="center" marginBottom="m" color="secondaryText">
              Position your face in the circle and follow the instructions. Remove masks or glasses for best results.
            </Text>
          </MotiView>

          {/* Camera Circle */}
          <MotiView
            from={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              width={250}
              height={250}
              borderRadius="xl"
              backgroundColor="cardPrimaryBackground"
              justifyContent="center"
              alignItems="center"
              borderWidth={4}
              borderColor={isCapturing ? "primaryAction" : "success"}
              marginBottom="l"
              overflow="hidden"
            >
              <CameraView
                ref={cameraRef}
                style={{ width: 180, height: 180, borderRadius: 90 }}
                facing="front"
                onCameraReady={() => setIsCameraReady(true)}
              />
              {!isCameraReady && (
                <View style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0, justifyContent: "center", alignItems: "center", backgroundColor: "rgba(0,0,0,0.2)" }}>
                  <ActivityIndicator size="large" color={theme.colors.primaryAction} />
                </View>
              )}
              {showLivenessDetection && !isCapturing && (
                <View style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0, justifyContent: "center", alignItems: "center", backgroundColor: "rgba(0,0,0,0.3)" }}>
                  <Feather name="user" size={60} color={theme.colors.primaryAction} />
                </View>
              )}
            </Box>
          </MotiView>

          {/* Current Instruction */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
            key={livenessStep}
          >
            <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l" width="100%">
              <Text variant="title2" textAlign="center" marginBottom="s">
                {isCapturing 
                  ? (livenessStep < livenessSteps.length ? livenessSteps[livenessStep].instruction : "Capturing...")
                  : "Ready to start facial verification"
                }
              </Text>
              <Text variant="body" fontSize={14} color="secondaryText" textAlign="center">
                {isCapturing
                  ? (livenessStep < livenessSteps.length
                      ? `Step ${livenessStep + 1} of ${livenessSteps.length}`
                      : "Processing your selfie...")
                  : "Tap the button below to begin"
                }
              </Text>
            </Box>
          </MotiView>

          {/* Progress Indicator */}
          {isCapturing && (
            <MotiView
              from={{ opacity: 0, translateY: 30 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ type: "timing", delay: 600 }}
            >
              <Box flexDirection="row" gap="s" marginBottom="l">
                {livenessSteps.map((_, index) => (
                  <Box
                    key={index}
                    width={40}
                    height={6}
                    backgroundColor={index <= livenessStep ? "success" : "cardBorder"}
                    borderRadius="s"
                  />
                ))}
              </Box>
            </MotiView>
          )}

          <MotiView
            from={{ opacity: 0, translateY: 40 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 800 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m" marginBottom="l" width="100%">
              <Text variant="body" fontSize={14} color="primaryAction" textAlign="center" fontWeight="600">
                🔒 Liveness Detection Active
              </Text>
              <Text variant="body" fontSize={12} color="secondaryText" textAlign="center" marginTop="xs">
                This ensures you're physically present and prevents spoofing
              </Text>
            </Box>
          </MotiView>

          {!isCapturing && !captureComplete && !captureFailed && (
            <MotiView
              from={{ translateY: 50, opacity: 0 }}
              animate={{ translateY: 0, opacity: 1 }}
              transition={{ type: "timing", delay: 1000 }}
            >
              <Button 
                label="🤳 Start Facial Verification" 
                onPress={handleStartLivenessDetection} 
                disabled={!isCameraReady}
                paddingHorizontal="l"
              />
            </MotiView>
          )}
        </Box>
      </SafeAreaView>
    </Box>
  )
}
