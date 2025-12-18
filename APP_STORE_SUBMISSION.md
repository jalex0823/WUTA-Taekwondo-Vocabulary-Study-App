# App Store / Play Store Submission Checklist (WUTA)

This document is a practical checklist for submitting the WUTA Taekwondo Vocabulary Trainer as a **native app wrapper**.

> ⚠️ Apple often rejects apps that are “just a website in a wrapper”.
> To improve acceptance odds, add at least one meaningful native feature (see section: "Native value").

## 1) Choose the wrapper approach

Recommended: **Capacitor** (WKWebView on iOS, Android WebView on Android).

- Wrapper project location: `mobile/`
- Config: `mobile/capacitor.config.ts` (`server.url` must be your HTTPS production site)

## 2) iOS App Store requirements

### A. Privacy / Tracking

- Confirm whether you collect any personal data.
  - If you **do not**: state “No data collected” in App Store Connect.
  - If you **do** (e.g., analytics): document it and add required disclosures.
- Avoid third‑party tracking SDKs.

### B. Kids category (if applicable)

- No external links that kids can tap into the open internet.
- No behavioral advertising.
- Clear parental gating if you add any external links.

### C. Audio behavior (iOS autoplay policies)

- Verify on device:
  - First visit: tapping 🔊 plays audio reliably.
  - Auto Guide: “Start” is a user action and should unlock audio.
  - Background music: enabling may require a tap; show clear UI feedback.

### D. Review account / server access

- If the app requires a login, provide a demo account.
- For WUTA: no login, but it depends on your hosted URL.
  - Ensure the production URL is stable and uses HTTPS.

## 3) Google Play requirements

### A. Data Safety form

- Document what data is collected/stored.
  - LocalStorage only (on-device) is usually not “collected”, but confirm.

### B. Content rating

- Likely “Everyone”.

## 4) Native value (to reduce Apple rejection risk)

Minimum recommended additions before final submission:

1) **Keep Screen Awake** while Auto Guide is running (native plugin) so the phone doesn’t sleep during training.
2) **Native haptics** (Capacitor Haptics) instead of relying on web vibration (iOS Safari often ignores vibration).

If you want, I can implement these with Capacitor plugins next.

## 5) Final smoke checklist (do this on real devices)

### iPhone

- Install the app build (TestFlight or device install).
- Verify:
  - Home → belt list scroll is smooth
  - Terms page controls don’t overlap
  - 🔊 plays audio after one tap
  - Auto Guide advances even if audio is blocked
  - Music toggle doesn’t double-toggle

### Android

- Same checks, plus:
  - Back button behavior
  - WebView audio permissions

## 6) Store assets

- App icon (1024×1024 for iOS, adaptive icon for Android)
- Screenshots:
  - Home screen
  - Flashcard screen
  - Auto Guide screen

## 7) Suggested reviewer notes (copy/paste)

- “Audio requires a user tap due to iOS autoplay policy. Tap 🔊 on any card or press Start Auto Play.”
- “This is a kid-friendly vocabulary practice tool. No login, no ads, no tracking.”
