# Open Payment - Mobile App (PayHack25 Demo)

This is the frontend for the Open Payment mobile application, built with React Native and Expo SDK 53. It showcases a polished, feature-rich user interface for a unified cross-border payment system, designed with a modern, minimalist aesthetic and smooth animations.

## 🚀 Features

- Dual login flows for personal users and merchants
- Dashboard with balance, quick actions, and recent transactions
- Cross-border QR simulation with real-time payment processing
- ESG-based T+ Tree investment feature with progress tracking
- Transaction history with FX savings and network labels
- Smooth animations using Moti + Reanimated
- Network support: DuitNow, PayNow, UPI, PromptPay, QRIS

## ⚙️ Tech Stack

- Expo SDK 53
- React Native 0.79.2
- React 19.0.0
- Hermes JS engine
- New Architecture enabled (Fabric + TurboModules)

### Core Libraries

- expo, expo-status-bar
- @shopify/restyle
- react-native-reanimated
- moti
- react-navigation

## 🛠 Prerequisites

- Node.js (LTS): https://nodejs.org/
- Expo Go App (iOS / Android): https://expo.dev/client
- Git

## 🧾 Setup Instructions
- npm install
- npm install react@19.0.0 react-dom@19.0.0 react-native@0.79.2
- npx expo install @shopify/restyle moti react-native-reanimated expo-status-bar
- npx expo start --clear
- or
- npx expo start
- Scan the QR code using Expo Go on your phone

The app will open with hot reload

📂 Project Structure
/theme – Theme config (colors, spacing)

/components – Reusable styled components

/context – Auth state handling

/navigation – Stack + tab navigation setup

/screens – All app screens

App.tsx – Main entry point

🧪 Usage Flow
Auth
Choose User or Merchant from welcome screen

Tap login to access dashboard

Scan & Pay
Go to Scan Tab

Tap Upload Random QR

Tap Scan & Pay

Watch real-time processing + routing

See success + FX savings + environmental impact

Wallet
View T+ Tree investment growth

Transaction history by network

ESG + FX savings tracking

⚠️ Compatibility Notes
Expo Go iOS enforces:

react-native@0.79.2

Hermes engine

New Architecture (Fabric) enabled

Do not use:

react-native@0.80.x (causes version mismatch)

raw #hex values in Restyle props (throws error)

Use only colors defined in theme.ts or fallback to style={{ backgroundColor: "#HEX" }}.

🧯 Troubleshooting
Issue	Solution
React Native version mismatch	Run npm install react-native@0.79.2
Hex color error	Add color to theme or use inline style
expo-status-bar missing	Run npx expo install expo-status-bar
Hermes crash	Ensure "jsEngine": "hermes" and "newArchEnabled": true
Metro stuck	Run npx expo start --clear
