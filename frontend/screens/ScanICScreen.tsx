"use client"
import { useState, useRef, useEffect } from "react"
import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Dimensions, Image, View, ActivityIndicator } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text, Button } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { CameraView, useCameraPermissions } from "expo-camera"

const { width } = Dimensions.get("window")

export default function ScanICScreen({ navigation }: { navigation: any }) {
  const theme = useTheme()
  const [permission, requestPermission] = useCameraPermissions()
  const [isCameraReady, setIsCameraReady] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [isCapturing, setIsCapturing] = useState(false)
  const cameraRef = useRef<CameraView | null>(null)

  const handleCapture = async () => {
    if (cameraRef.current && isCameraReady && !isCapturing) {
      setIsCapturing(true)
      try {
        const photo = await cameraRef.current.takePictureAsync({ quality: 0.8, base64: false })
        setCapturedImage(photo.uri)
        setShowPreview(true)
      } catch (e) {
        console.log('Error taking picture:', e)
      } finally {
        setIsCapturing(false)
      }
    }
  }

  const handleRetake = () => {
    setShowPreview(false)
    setCapturedImage(null)
  }

  const handleConfirm = () => {
    // Create mock IC data structure that matches what ConfirmDetailsScreen expects
    const icData = {
      name: "ALI BIN HASSAN",
      nric: "901234-56-7890",
      dateOfBirth: "12 JAN 1990",
      address: "NO 123, JALAN BUKIT BINTANG, 50200 KUALA LUMPUR",
      nationality: "WARGANEGARA",
      religion: "ISLAM",
      gender: "LELAKI",
      image: capturedImage // Include the captured IC image
    }
    
    navigation.navigate("FacialVerification", { icData })
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
          We need your permission to show the camera
        </Text>
        <Button 
          label="Grant Permission" 
          onPress={requestPermission} 
          marginTop="l"
        />
      </Box>
    )
  }

  if (showPreview && capturedImage) {
    return (
      <Box flex={1} backgroundColor="mainBackground">
        <SafeAreaView style={{ flex: 1 }}>
          <Box flexDirection="row" alignItems="center" padding="l" backgroundColor="cardPrimaryBackground">
            <TouchableOpacity onPress={() => navigation.goBack()}>
              <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
            </TouchableOpacity>
            <Text variant="title1" marginLeft="m">Confirm IC Photo</Text>
          </Box>
          <Box flex={1} padding="l" justifyContent="center" alignItems="center">
            <Image
              source={{ uri: capturedImage }}
              style={{ width: width - 60, height: (width - 60) * 0.63, borderRadius: 12, marginBottom: 24 }}
              resizeMode="cover"
            />
            <Box flexDirection="row" gap="m" width="100%">
              <Box flex={1}>
                <Button label="Retake Photo" onPress={handleRetake} variant="outline" />
              </Box>
              <Box flex={1}>
                <Button label="Confirm & Continue" onPress={handleConfirm} />
              </Box>
            </Box>
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
          <Text variant="title1" marginLeft="m">Scan Your IC</Text>
        </Box>
        <Box flex={1} justifyContent="center" alignItems="center" padding="l">
          <MotiView
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "timing" }}
          >
            <Text variant="title2" textAlign="center" marginBottom="m">Step 1 of 3: Identity Card</Text>
            <Text variant="body" textAlign="center" marginBottom="xl" color="secondaryText">
              Place your Malaysian IC (MyKad) within the frame and ensure all details are clearly visible
            </Text>
          </MotiView>
          <MotiView
            from={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "timing", delay: 200 }}
          >
            <Box
              width={width - 60}
              height={(width - 60) * 0.63}
              backgroundColor="cardPrimaryBackground"
              borderRadius="m"
              justifyContent="center"
              alignItems="center"
              borderWidth={3}
              borderColor="primaryAction"
              marginBottom="l"
              overflow="hidden"
            >
              <CameraView
                ref={cameraRef}
                style={{ width: "100%", height: "100%" }}
                facing="back"
                onCameraReady={() => setIsCameraReady(true)}
              />
              {!isCameraReady && (
                <View style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0, justifyContent: "center", alignItems: "center", backgroundColor: "rgba(0,0,0,0.2)" }}>
                  <ActivityIndicator size="large" color={theme.colors.primaryAction} />
                </View>
              )}
            </Box>
          </MotiView>
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
          >
            <Box backgroundColor="blueLight" padding="m" borderRadius="m" marginBottom="l" width="100%">
              <Text variant="body" fontSize={14} color="primaryAction" textAlign="center" fontWeight="600">
                💡 Tips for best results:
              </Text>
              <Text variant="body" fontSize={12} color="secondaryText" textAlign="center" marginTop="xs">
                • Ensure good lighting • Remove any covers • Keep IC flat • Avoid shadows
              </Text>
            </Box>
          </MotiView>
          <MotiView
            from={{ translateY: 30, opacity: 0 }}
            animate={{ translateY: 0, opacity: 1 }}
            transition={{ type: "timing", delay: 600 }}
          >
            <Button 
              label={isCapturing ? "Capturing..." : "📷 Capture IC"} 
              onPress={handleCapture} 
              disabled={!isCameraReady || isCapturing}
              paddingHorizontal="l"
            />
          </MotiView>
        </Box>
      </SafeAreaView>
    </Box>
  )
}
