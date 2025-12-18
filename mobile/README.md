# WUTA Mobile Wrapper (Capacitor)

This folder contains a **native wrapper** for submitting WUTA to the **Apple App Store** and **Google Play**.

It uses **Capacitor** to load the hosted web app inside a native WebView.

## Prereqs

- Node.js LTS
- Xcode (for iOS builds)
- Android Studio (for Android builds)
- A deployed HTTPS production URL for the Flask app

## 1) Install dependencies

From repo root:

- `cd mobile`
- `npm install`

## 2) Set the production URL

Edit `mobile/capacitor.config.ts`:

- Set `server.url` to your HTTPS production site URL.

## 3) Add native platforms

- `npm run cap:add:ios`
- `npm run cap:add:android`

## 4) Sync

- `npm run cap:sync`

## 5) Open and build

- iOS: `npm run cap:open:ios`
- Android: `npm run cap:open:android`

## Review notes (important for approval)

- Audio is **user-gesture driven** (required by iOS policy). Users tap 🔊 or start Auto Guide.
- Background music is OFF/ON via a toggle; iOS may require a tap after enabling.
- The app is kid-friendly: no user chat, no ads, no external links.

## Tip: Avoid “website-in-a-wrapper” rejection

Add at least one **native value** before final submission. Suggested low-risk options:

- Home-screen quick actions (native)
- “Keep Screen Awake” (native)
- Better haptics via Capacitor plugins

See `APP_STORE_SUBMISSION.md` in repo root for a full checklist.
