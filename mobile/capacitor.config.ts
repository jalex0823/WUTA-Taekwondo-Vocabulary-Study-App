import type { CapacitorConfig } from '@capacitor/cli';

// IMPORTANT:
// - Set server.url to your production URL (https) before building.
// - This wrapper loads the hosted Flask app inside a native WebView.
// - Apple will reject “just a website in a wrapper” unless it provides value.
//   This app does: offline installability, full-screen experience, and kid-friendly training UI.

const config: CapacitorConfig = {
  appId: 'com.wuta.taekwondo.vocab',
  appName: 'WUTA Taekwondo',
  webDir: 'www',
  bundledWebRuntime: false,

  // Load the live site.
  // Replace with your real production URL.
  server: {
    url: 'https://YOUR-PRODUCTION-URL-HERE',
    cleartext: false
  }
};

export default config;
