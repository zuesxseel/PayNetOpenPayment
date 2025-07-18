import type React from "react";
import {
  createBox,
  createText,
  createRestyleComponent,
  createVariant,
} from "@shopify/restyle";
import type { Theme } from "../theme/theme";
import { TouchableOpacity } from "react-native";

export const Box = createBox<Theme>();
export const Text = createText<Theme>();

interface ButtonProps {
  onPress: () => void;
  label: string;
  variant?: "primary" | "outline" | "secondary";
  disabled?: boolean;
  [key: string]: any;
}

export const Button = ({
  onPress,
  label,
  variant = "primary",
  disabled = false,
  ...rest
}: ButtonProps) => {
  const getBackgroundColor = () => {
    if (variant === "primary") return "primaryAction";
    if (variant === "outline") return "cardPrimaryBackground";
    return "cardPrimaryBackground";
  };

  const getTextColor = () => {
    if (variant === "primary") return "primaryActionText";
    if (variant === "outline") return "primaryAction";
    return "secondaryActionText";
  };

  return (
    <TouchableOpacity
      onPress={disabled ? undefined : onPress}
      disabled={disabled}
    >
      <Box
        backgroundColor={getBackgroundColor()}
        paddingVertical="m"
        borderRadius="l"
        alignItems="center"
        borderWidth={variant === "outline" ? 1 : 0}
        borderColor={variant === "outline" ? "primaryAction" : "cardBorder"}
        opacity={disabled ? 0.5 : 1}
        {...rest}
      >
        <Text variant="button" color={getTextColor()}>
          {label}
        </Text>
      </Box>
    </TouchableOpacity>
  );
};

// Note: useTheme should be imported directly from @shopify/restyle, not from here
// import { useTheme } from "@shopify/restyle"
