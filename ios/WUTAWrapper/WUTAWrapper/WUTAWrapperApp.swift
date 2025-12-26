import SwiftUI

@main
struct WUTAWrapperApp: App {
    /// Your hosted Flask app base URL (must be HTTPS for App Store submission).
    static let BASE_URL = URL(string: "https://YOUR-DOMAIN-HERE.example")!

    @StateObject private var subscriptionManager = SubscriptionManager()

    var body: some Scene {
        WindowGroup {
            RootView(baseURL: Self.BASE_URL)
                .environmentObject(subscriptionManager)
                .task {
                    await subscriptionManager.initialize()
                }
        }
    }
}
