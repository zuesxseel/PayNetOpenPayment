import type React from "react"
import { createBox, createText, createRestyleComponent, createVariant } from "@shopify/restyle"
import type { Theme } from "../theme/theme"
import { TouchableOpacity } from "react-native"

export const Box = createBox<Theme>()
export const Text = createText<Theme>()

export const Card = createRestyleComponent<
  React.ComponentProps<typeof Box> & { variant?: "default" | "elevated" },
  Theme
>([createVariant({ themeKey: "cardVariants" })], Box)

Card.defaultProps = {
  variant: "default",
}

export const Button = ({ onPress, label, variant = "primary", ...rest }) => {
  return (
    <TouchableOpacity onPress={onPress}>
      <Box
        backgroundColor={variant === "primary" ? "primaryAction" : "cardPrimaryBackground"}
        paddingVertical="m"
        borderRadius="l"
        alignItems="center"
        borderWidth={variant === "outline" ? 1 : 0}
        borderColor="cardBorder"
        {...rest}
      >
        <Text variant="button" color={variant === "primary" ? "primaryActionText" : "secondaryActionText"}>
          {label}
        </Text>
      </Box>
    </TouchableOpacity>
  )
}

// Note: useTheme should be imported directly from @shopify/restyle, not from here
// import { useTheme } from "@shopify/restyle"
