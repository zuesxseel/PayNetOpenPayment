# Open Payment - Mobile App (PayHack25 Demo)

This is the frontend for the Open Payment mobile application, built with React Native and Expo. It showcases a polished, feature-rich user interface for a unified cross-border payment system, designed with a modern, minimalist aesthetic and smooth animations.

## Features

- **Dual Login Flows**: Separate, beautifully designed login pages for personal users and merchants.
- **Complete Dashboard**: A central hub for balance, quick actions, and recent transactions.
- **Cross-Border QR Simulation**: A full user flow from scanning a QR code to payment confirmation.
- **Transaction Processing**: Realistic payment flow with processing screens and success confirmations.
- **Multi-Network Support**: Support for DuitNow, PayNow, UPI, PromptPay, and QRIS networks.
- **T+ Tree Investment**: Complete ESG investment feature with progress tracking.
- **Transaction History**: Detailed transaction history with cross-border savings tracking.
- **Polished UI/UX**: A refined design system with custom components, gradients, and smooth animations.

## Core Libraries

This project leverages modern libraries to achieve a high-quality result:

- **React Navigation**: For robust and type-safe navigation.
- **Shopify Restyle**: For a themeable, type-safe design system that ensures UI consistency.
- **Moti & Reanimated**: For fluid, performant animations.
- **Expo**: For the underlying framework and development tools.

---

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js (LTS version)**: [Download Node.js](https://nodejs.org/)
2. **Expo Go App**: Install the Expo Go app on your iOS or Android device.
    - [Download for iOS](https://apps.apple.com/us/app/expo-go/id982107779)
    - [Download for Android](https://play.google.com/store/apps/details?id=host.exp.exponent)
3. **Git**: To clone the repository.

---

## How to Launch the App

Follow these steps to get the application running on your device via Expo Go.

### 1. Clone the Repository

First, clone this project to your local machine.

\`\`\`bash
git clone <your-repository-url>
cd open-payment-app
\`\`\`

### 2. Install Dependencies

This project uses npm to manage packages. Run the following command in the project's root directory to install all the required dependencies listed in `package.json`.

\`\`\`bash
npm install
\`\`\`

**Important**: Make sure to install the additional required libraries:

\`\`\`bash
npx expo install @shopify/restyle moti react-native-reanimated
\`\`\`

### 3. Start the Development Server

Once the dependencies are installed, you can start the Expo development server.

\`\`\`bash
npx expo start
\`\`\`

This command will do two things:
- Start the Metro Bundler, which compiles your JavaScript code.
- Open a new tab in your web browser with the Expo Developer Tools, which will display a QR code.

### 4. Run on Your Device

1. Open the **Expo Go** app on your iOS or Android phone.
2. On the "Home" tab, tap **"Scan QR Code"**.
3. Point your device's camera at the QR code displayed in your browser or terminal.

Expo Go will then download and run the app on your device. Any changes you make to the code will automatically reload in the app.

---

## How to Use

### Authentication Flow
- The app starts on the **Welcome Screen**.
- Choose **"Login as User"** for personal account or **"Merchant Portal"** for business account.
- Click the login button to simulate a successful login and access the main app.

### Main Features
- **Home Tab**: View balance, quick actions, and recent transactions.
- **Scan Tab**: 
  - Use "Upload Random QR" to generate different network QR codes (DuitNow, PayNow, UPI, PromptPay, QRIS).
  - Click "Scan & Pay" to process the payment and see the cross-border routing in action.
- **Wallet Tab**: 
  - View detailed balance information.
  - Access "T+ Tree Investment" to see your ESG investment progress.
  - View "Transaction History" with cross-border savings tracking.
- **Profile Tab**: Account settings and logout functionality.

### Payment Flow
1. Go to Scan tab
2. Click "Upload Random QR" to generate a sample QR from different networks
3. Click "Scan & Pay" to start the payment process
4. Watch the processing screen show network routing
5. See the success screen with FX savings and environmental impact

---

## Project Structure

The project is organized into the following directories:

- `/theme`: Design system theme configuration using Shopify Restyle.
- `/components`: Reusable UI components built with the theme system.
- `/context`: React Context for authentication state management.
- `/navigation`: React Navigation setup (stacks, tabs).
- `/screens`: Individual screen components for the app.
- `App.tsx`: The main entry point of the application.

---

## New Features Added

### Complete Navigation Flow
- Fixed merchant portal navigation
- Added proper stack navigation for scan and wallet flows
- Implemented payment processing and success screens

### Enhanced Payment Experience
- Multi-network QR code support (DuitNow, PayNow, UPI, PromptPay, QRIS)
- Realistic payment processing with network-specific routing
- Cross-border FX savings calculation and display
- Environmental impact tracking (T+ Tree contributions)

### Comprehensive Wallet Features
- Complete T+ Tree investment page with progress tracking
- Detailed transaction history with network indicators
- Cross-border savings analytics
- Visual tree growth representation

### Improved User Experience
- Smooth animations throughout the app
- Network-specific color coding
- Realistic transaction data and scenarios
- Professional merchant vs user account differentiation

---

## Troubleshooting

If you encounter any issues:

1. **Navigation errors**: Make sure all screen imports are correct and navigation stacks are properly configured.
2. **Blank screen after login**: Ensure all dependencies are installed correctly, especially `@shopify/restyle`, `moti`, and `react-native-reanimated`.
3. **Animation issues**: Ensure `react-native-reanimated` is properly installed and configured.
4. **Build errors**: Try deleting `node_modules` and running `npm install` again.
5. **QR processing errors**: Check that the QR payload is valid JSON format.

For any other issues, clear your Expo cache with `npx expo start --clear`.
