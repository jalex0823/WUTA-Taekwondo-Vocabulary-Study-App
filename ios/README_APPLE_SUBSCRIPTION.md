# WUTA iOS Wrapper + App Store Connect (Subscriptions)

This repository is a Flask web app. To publish on the Apple App Store you need an iOS app.

This folder provides a **SwiftUI wrapper** approach:
- iOS app shows your hosted website via `WKWebView`.
- A **StoreKit 2 auto-renewable subscription** gates access.

> Note: You must use **macOS + Xcode** to build/sign/upload to App Store Connect.

---

## 1) App Store Connect setup (7-day trial + $0.99 recurring)

### A. Create the app record
1. Join the Apple Developer Program.
2. App Store Connect → **My Apps** → **+** → New App.
3. Pick a **Bundle ID** you will also use in Xcode.

### B. Create the subscription
1. App Store Connect → your app → **Subscriptions**.
2. Create a **Subscription Group** (e.g., `WUTA Premium`).
3. Create an **Auto-Renewable Subscription** product:
   - Duration: usually **1 Month** (or your desired recurring period)
   - Price: pick the **$0.99** price point (Apple manages tiers/price points)
   - Add localization (Display Name + Description)
4. Add an **Introductory Offer**:
   - Type: **Free**
   - Duration: **7 Days**

### C. Agreements & banking
App Store Connect → **Agreements, Tax, and Banking**: complete everything needed for paid IAP.

### D. Sandbox testing
App Store Connect → Users and Access → Sandbox Testers.

---

## 2) iOS wrapper implementation (SwiftUI + StoreKit 2)

### What’s included
- `ios/WUTAWrapper/WUTAWrapper/...` contains Swift files you can drop into an Xcode project.
- You will still create an Xcode project on a Mac.

### Create the Xcode project
1. Xcode → File → New → Project → **App** (iOS)
2. Interface: **SwiftUI**
3. Product Name: `WUTAWrapper`
4. Bundle Identifier: match the Bundle ID from App Store Connect

### Add the source files
Copy the contents of:
- `ios/WUTAWrapper/WUTAWrapper/WUTAWrapperApp.swift`
- `ios/WUTAWrapper/WUTAWrapper/Views/*`
- `ios/WUTAWrapper/WUTAWrapper/Store/*`
into your Xcode project (same folder structure is fine).

### Configure your web URL
Edit `BASE_URL` in `WUTAWrapperApp.swift` to point at your hosted HTTPS site.

### Configure your subscription Product ID
Edit `SUBSCRIPTION_PRODUCT_ID` in `SubscriptionManager.swift` to the product id from App Store Connect.

---

## 3) Review checklist (common rejection avoiders)

- Provide **Privacy Policy URL** and **Support URL** in App Store Connect.
- Complete the **App Privacy** questionnaire.
- If you use subscriptions, Apple expects:
  - Clear pricing and renewal wording
  - Restore purchases button
  - Links to Terms/Privacy

---

## 4) Important note about “paywalling a website”

This wrapper gates access *in the app*. If your website is publicly accessible, users could still visit it outside the app.

If you need strong enforcement, you’ll want a backend flow:
- iOS app purchases → receipt validation (App Store Server API) → your server issues a session token → WebView loads with token.

That’s doable, but it’s a larger build.
