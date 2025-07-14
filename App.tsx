import { StatusBar } from "expo-status-bar"
import { SafeAreaProvider } from "react-native-safe-area-context"
import { ThemeProvider } from "@shopify/restyle"
import AppNavigator from "./navigation/AppNavigator"
import theme from "./theme/theme"
import { AuthProvider } from "./context/AuthContext"

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <StatusBar style="dark" />
          <AppNavigator />
        </ThemeProvider>
      </AuthProvider>
    </SafeAreaProvider>
  )
}
