import type React from "react"
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, View } from "react-native"
import { LinearGradient } from "expo-linear-gradient"
import { Colors } from "../constants/Colors"

type AppButtonProps = {
  title: string
  onPress: () => void
  variant?: "primary" | "secondary" | "outline"
  loading?: boolean
  disabled?: boolean
  icon?: React.ReactNode
}

export const AppButton = ({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
  icon,
}: AppButtonProps) => {
  const textStyle = [styles.text, variant === "outline" && styles.textOutline]

  const ButtonContent = () => (
    <>
      {loading ? (
        <ActivityIndicator color={variant === "outline" ? Colors.primary : Colors.white} />
      ) : (
        <View style={styles.content}>
          {icon}
          <Text style={textStyle}>{title}</Text>
        </View>
      )}
    </>
  )

  if (variant === "primary") {
    return (
      <TouchableOpacity onPress={onPress} disabled={disabled || loading} style={styles.touchable}>
        <LinearGradient
          colors={[Colors.primary, Colors.primaryDark]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[styles.button, disabled && styles.disabled]}
        >
          <ButtonContent />
        </LinearGradient>
      </TouchableOpacity>
    )
  }

  return (
    <TouchableOpacity
      style={[styles.button, styles[variant], disabled && styles.disabled]}
      onPress={onPress}
      disabled={disabled || loading}
    >
      <ButtonContent />
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  touchable: {
    borderRadius: 14,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  button: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  primary: {},
  secondary: { backgroundColor: Colors.secondary },
  outline: { backgroundColor: Colors.white, borderWidth: 1.5, borderColor: Colors.border },
  disabled: { opacity: 0.5 },
  content: { flexDirection: "row", alignItems: "center", justifyContent: "center" },
  text: { fontSize: 17, fontWeight: "600", color: Colors.white, marginLeft: 8 },
  textOutline: { color: Colors.text },
})
