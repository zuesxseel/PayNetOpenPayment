import type React from "react"
import { View, StyleSheet } from "react-native"
import { Colors } from "../constants/Colors"

export const AppCard = ({ children, style }: { children: React.ReactNode; style?: object }) => {
  return <View style={[styles.card, style]}>{children}</View>
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.white,
    borderRadius: 18,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 5,
  },
})
