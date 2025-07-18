"use client"

import { SafeAreaView } from "react-native-safe-area-context"
import { TouchableOpacity, Alert, Dimensions, ScrollView } from "react-native"
import { Feather } from "@expo/vector-icons"
import { Box, Text } from "../components/Themed"
import { useTheme } from "@shopify/restyle"
import { MotiView } from "moti"
import { useState, useRef, useEffect } from "react"
import { WebView } from "react-native-webview"
import { mockVerifyRecaptcha } from "../lib/recaptcha"

interface UEBAVerificationScreenProps {
  navigation: any
  route: any
}

export default function UEBAVerificationScreen({ navigation, route }: UEBAVerificationScreenProps) {
  const theme = useTheme()
  const { notification } = route.params || {}
  const [captchaToken, setCaptchaToken] = useState("")
  const [isVerifying, setIsVerifying] = useState(false)
  const [showCaptcha, setShowCaptcha] = useState(false)
  const [attempts, setAttempts] = useState(0)
  const webViewRef = useRef<WebView>(null)
  const { width, height } = Dimensions.get("window")

  // reCAPTCHA site key from environment variables
  const RECAPTCHA_SITE_KEY = process.env.EXPO_PUBLIC_RECAPTCHA_SITE_KEY || "6LekVIYrAAAAADF_yyhxH0izQY9bn-iP85H1BCir"

  const recaptchaHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}"></script>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          margin: 0;
          padding: 15px;
          background-color: #f8f9fa;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          box-sizing: border-box;
        }
        .container {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
          text-align: center;
          width: 100%;
          max-width: 320px;
          box-sizing: border-box;
        }
        .title {
          color: #333;
          margin-bottom: 15px;
          font-size: 18px;
          font-weight: 600;
          line-height: 1.3;
        }
        .subtitle {
          color: #666;
          margin-bottom: 25px;
          font-size: 14px;
          line-height: 1.4;
        }
        .verify-btn {
          background: #4285f4;
          color: white;
          border: none;
          padding: 14px 20px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s;
          width: 100%;
          box-sizing: border-box;
        }
        .verify-btn:hover {
          background: #3367d6;
        }
        .verify-btn:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
        .status {
          margin-top: 15px;
          padding: 12px;
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.3;
        }
        .status.success {
          background: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }
        .status.error {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }
        .status.loading {
          background: #fff3cd;
          color: #856404;
          border: 1px solid #ffeaa7;
        }
        .spinner {
          display: inline-block;
          width: 18px;
          height: 18px;
          border: 2px solid #f3f3f3;
          border-top: 2px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 8px;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .security-icon {
          font-size: 24px;
          margin-bottom: 10px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="security-icon">🔐</div>
        <div class="title">Security Verification</div>
        <div class="subtitle">Please verify you're human to continue with your transaction</div>
        
        <button id="verify-btn" class="verify-btn" onclick="executeRecaptcha()">
          Verify I'm Human
        </button>
        
        <div id="status" class="status" style="display: none;"></div>
      </div>

      <script>
        let isVerifying = false;

        function showStatus(message, type) {
          const statusDiv = document.getElementById('status');
          statusDiv.innerHTML = message;
          statusDiv.className = 'status ' + type;
          statusDiv.style.display = 'block';
        }

        function executeRecaptcha() {
          if (isVerifying) return;
          
          isVerifying = true;
          const btn = document.getElementById('verify-btn');
          btn.disabled = true;
          btn.innerHTML = '<span class="spinner"></span>Verifying...';
          
          showStatus('Processing verification...', 'loading');

          grecaptcha.ready(function() {
            grecaptcha.execute('${RECAPTCHA_SITE_KEY}', {action: 'verify'}).then(function(token) {
              // Send token to React Native
              window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'captcha_success',
                token: token,
                score: 'pending'
              }));
              
              showStatus('✅ Verification successful!', 'success');
              
              setTimeout(() => {
                isVerifying = false;
                btn.disabled = false;
                btn.innerHTML = 'Verify I\\'m Human';
                document.getElementById('status').style.display = 'none';
              }, 2000);
              
            }).catch(function(error) {
              console.error('reCAPTCHA error:', error);
              showStatus('❌ Verification failed. Please try again.', 'error');
              
              window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'captcha_error',
                error: error.message
              }));
              
              setTimeout(() => {
                isVerifying = false;
                btn.disabled = false;
                btn.innerHTML = 'Verify I\\'m Human';
              }, 3000);
            });
          });
        }
      </script>
    </body>
    </html>
  `

  const handleWebViewMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data)

      switch (data.type) {
        case "captcha_success":
          setCaptchaToken(data.token)
          setIsVerifying(true)
          verifyCaptchaToken(data.token)
          break
        case "captcha_error":
          Alert.alert("reCAPTCHA Error", "Verification failed. Please try again.")
          setCaptchaToken("")
          setIsVerifying(false)
          break
        default:
          console.log("Unknown message type:", data.type)
      }
    } catch (error) {
      console.error("Error parsing WebView message:", error)
      Alert.alert("Error", "Something went wrong. Please try again.")
    }
  }

  const verifyCaptchaToken = async (token: string) => {
    try {
      // Use the API utility to verify the token
      const result = await mockVerifyRecaptcha(token)

      setIsVerifying(false)

      if (result.success && result.score >= 0.5) {
        const paymentAmount = notification?.amount?.replace("RM ", "") || "87.79"
        Alert.alert(
          "Verification Successful! ✅",
          `Your identity has been verified (Score: ${result.score.toFixed(2)}). Payment of RM ${paymentAmount} has been processed successfully.`,
          [
            {
              text: "Continue",
              onPress: () =>
                navigation.navigate("PaymentSuccess", {
                  qrData: {
                    merchantName: notification?.merchant || "Unknown Merchant",
                    amount: paymentAmount,
                    currency: "MYR",
                    type: "UEBA Verified",
                  },
                }),
            },
          ],
        )
      } else {
        throw new Error(`Verification failed. Score: ${result.score?.toFixed(2) || "N/A"}`)
      }
    } catch (error) {
      setIsVerifying(false)
      setAttempts((prev) => prev + 1)

      if (attempts >= 2) {
        Alert.alert(
          "Too Many Failed Attempts",
          "Your account has been temporarily locked for security reasons. Please contact support.",
          [{ text: "OK", onPress: () => navigation.navigate("Home") }],
        )
      } else {
        Alert.alert(
          "Verification Failed",
          `${error instanceof Error ? error.message : "Unknown error"}. ${3 - attempts - 1} attempts remaining.`,
        )
        setCaptchaToken("")
        setShowCaptcha(false)
        setTimeout(() => setShowCaptcha(true), 500)
      }
    }
  }

  const startCaptchaVerification = () => {
    setShowCaptcha(true)
  }

  useEffect(() => {
    // Auto-start captcha after component mounts
    setTimeout(() => {
      setShowCaptcha(true)
    }, 1000)
  }, [])

  return (
    <Box flex={1} backgroundColor="mainBackground">
      <SafeAreaView style={{ flex: 1 }}>
        <Box flexDirection="row" alignItems="center" justifyContent="space-between" padding="l">
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Feather name="arrow-left" size={24} color={theme.colors.primaryText} />
          </TouchableOpacity>
          <Text variant="title2" color="primaryText">
            UEBA Verification
          </Text>
          <Box width={24} />
        </Box>

        <ScrollView 
          style={{ flex: 1 }}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ flexGrow: 1, padding: 24 }}
        >
          {/* Alert Section */}
          <MotiView
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing" }}
          >
            <Box backgroundColor="dangerLight" padding="l" borderRadius="m" marginBottom="l">
              <Box flexDirection="row" alignItems="flex-start" marginBottom="m">
                <Box marginRight="m" marginTop="xs">
                  <Feather name="alert-triangle" size={24} color={theme.colors.error} />
                </Box>
                <Box flex={1}>
                  <Text variant="body" fontWeight="600" color="error" marginBottom="xs">
                    Suspicious Activity Detected
                  </Text>
                  <Text variant="body" fontSize={14} color="secondaryText" lineHeight={20}>
                    We detected a login attempt from a foreign location. RM {notification?.amount?.replace("RM ", "") || "87.79"} of pending transaction requires verification to proceed.
                  </Text>
                </Box>
              </Box>
            </Box>
          </MotiView>

          {/* Transaction Details */}
          {notification && (
            <MotiView
              from={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "timing", delay: 200 }}
            >
              <Box backgroundColor="cardPrimaryBackground" padding="l" borderRadius="m" marginBottom="l">
                <Text variant="body" fontWeight="600" color="primaryText" marginBottom="m">
                  Transaction Details
                </Text>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Merchant
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="600">
                    {notification.merchant}
                  </Text>
                </Box>
                <Box flexDirection="row" justifyContent="space-between" marginBottom="s">
                  <Text variant="body" color="secondaryText">
                    Amount
                  </Text>
                  <Text variant="body" color="primaryText" fontWeight="600">
                    {notification.amount}
                  </Text>
                </Box>
                {notification.location && (
                  <Box flexDirection="row" justifyContent="space-between">
                    <Text variant="body" color="secondaryText">
                      Location
                    </Text>
                    <Text variant="body" color="error" fontWeight="600">
                      {notification.location}
                    </Text>
                  </Box>
                )}
              </Box>
            </MotiView>
          )}

          {/* Verification Section */}
          <MotiView
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: "timing", delay: 400 }}
            style={{ flex: 1, minHeight: 400 }}
          >
            <Box backgroundColor="cardPrimaryBackground" borderRadius="m" padding="l" style={{ overflow: "hidden", minHeight: 350 }}>
              {!showCaptcha ? (
                <Box alignItems="center" justifyContent="center" flex={1}>
                  <Box
                    width={80}
                    height={80}
                    borderRadius="xl"
                    backgroundColor="blueLight"
                    justifyContent="center"
                    alignItems="center"
                    marginBottom="l"
                  >
                    <Feather name="shield" size={40} color={theme.colors.primaryAction} />
                  </Box>
                  <Text variant="body" color="secondaryText" marginBottom="l" textAlign="center">
                    Click below to start verification
                  </Text>
                  <TouchableOpacity onPress={startCaptchaVerification}>
                    <Box
                      backgroundColor="primaryAction"
                      paddingVertical="m"
                      paddingHorizontal="xl"
                      borderRadius="l"
                      alignItems="center"
                      flexDirection="row"
                      justifyContent="center"
                      gap="s"
                    >
                      <Feather name="shield" size={16} color={theme.colors.primaryActionText} />
                      <Text variant="body" color="primaryActionText" fontWeight="600">
                        Start Verification
                      </Text>
                    </Box>
                  </TouchableOpacity>
                </Box>
              ) : (
                <Box flex={1}>
                  <Text variant="body" color="secondaryText" marginBottom="m" textAlign="center">
                    Please complete the reCAPTCHA verification
                  </Text>
                  <Box 
                    flex={1} 
                    minHeight={300}
                    style={{ 
                      marginHorizontal: 10, 
                      marginBottom: -12,
                      borderRadius: 12,
                      overflow: "hidden"
                    }}
                  >
                    <WebView
                      ref={webViewRef}
                      source={{ html: recaptchaHtml }}
                      style={{ flex: 1 }}
                      onMessage={handleWebViewMessage}
                      javaScriptEnabled={true}
                      domStorageEnabled={true}
                      startInLoadingState={true}
                      scalesPageToFit={true}
                      originWhitelist={["*"]}
                    />
                  </Box>               
                </Box>
              )}

              {/* Loading Overlay */}
              {isVerifying && (
                <Box
                  position="absolute"
                  top={0}
                  left={0}
                  right={0}
                  bottom={0}
                  justifyContent="center"
                  alignItems="center"
                  style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
                  borderRadius="m"
                >
                  <Box backgroundColor="cardPrimaryBackground" padding="xl" borderRadius="l" alignItems="center">
                    <Text variant="body" color="primaryText" marginBottom="m">
                      Verifying...
                    </Text>
                    <MotiView
                      from={{ rotate: "0deg" }}
                      animate={{ rotate: "360deg" }}
                      transition={{
                        type: "timing",
                        duration: 1000,
                        loop: true,
                      }}
                    >
                      <Feather name="loader" size={24} color={theme.colors.primaryAction} />
                    </MotiView>
                  </Box>
                </Box>
              )}
            </Box>
          </MotiView>

          {/* Attempts Counter */}
          {attempts > 0 && (
            <MotiView from={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ type: "timing" }}>
              <Box marginTop="m" alignItems="center">
                <Text variant="body" color="error" fontSize={12}>
                  Failed attempts: {attempts}/3
                </Text>
              </Box>
            </MotiView>
          )}
        </ScrollView>
      </SafeAreaView>
    </Box>
  )
}
