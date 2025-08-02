import { StatusBar } from "expo-status-bar"
import { SafeAreaProvider } from "react-native-safe-area-context"
import { ThemeProvider } from "@shopify/restyle"
import AppNavigator from "./navigation/AppNavigator"
import theme from "./theme/theme"
import { AuthProvider } from "./context/AuthContext"
import { ZKPProvider } from "./context/ZKPContext"

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <ZKPProvider>
          <ThemeProvider theme={theme}>
            <StatusBar style="dark" />
            <AppNavigator />
          </ThemeProvider>
        </ZKPProvider>
      </AuthProvider>
    </SafeAreaProvider>
  )
}
