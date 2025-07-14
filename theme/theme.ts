import { createTheme } from "@shopify/restyle"

const palette = {
  bluePrimary: "#0A57E7",
  blueDark: "#003BBD",
  blueLight: "#F0F5FF",
  greenSuccess: "#00C48C",
  greenLight: "#E6F9F4",
  black: "#0C0D0F",
  white: "#FFFFFF",
  gray1: "#F7F8FA",
  gray2: "#E5E7EB",
  gray3: "#6B7280",
  redError: "#FF4D4F",
  orangeWarning: "#FF8C00",
}

const theme = createTheme({
  colors: {
    mainBackground: palette.gray1,
    cardPrimaryBackground: palette.white,
    primaryAction: palette.bluePrimary,
    primaryActionText: palette.white,
    secondaryActionText: palette.bluePrimary,
    primaryText: palette.black,
    secondaryText: palette.gray3,
    cardBorder: palette.gray2,
    success: palette.greenSuccess,
    error: palette.redError,
    warning: palette.orangeWarning,
    gradientStart: palette.bluePrimary,
    gradientEnd: palette.blueDark,
    // Add missing colors that were causing Restyle errors
    blueLight: palette.blueLight,
    greenLight: palette.greenLight,
    // Network-specific colors
    duitNowOrange: "#FF6B35",
    payNowGreen: "#00A651",
    upiOrange: "#FF9933",
    promptPayBlue: "#1E88E5",
    qrisRed: "#E53E3E",
    // Tree colors
    treeTrunk: "#8B5A2B",
    treeGreen: "#4CAF50",
  },
  spacing: {
    xs: 4,
    s: 8,
    m: 16,
    l: 24,
    xl: 40,
  },
  borderRadii: {
    s: 4,
    m: 10,
    l: 20,
    xl: 30,
  },
  textVariants: {
    hero: {
      fontSize: 36,
      fontWeight: "bold",
      color: "primaryText",
    },
    title1: {
      fontSize: 28,
      fontWeight: "bold",
      color: "primaryText",
    },
    title2: {
      fontSize: 22,
      fontWeight: "bold",
      color: "primaryText",
    },
    body: {
      fontSize: 16,
      lineHeight: 24,
      color: "secondaryText",
    },
    button: {
      fontSize: 16,
      fontWeight: "600",
      color: "primaryActionText",
    },
    defaults: {
      // We can define a default text variant here.
    },
  },
  breakpoints: {},
})

export type Theme = typeof theme
export default theme
