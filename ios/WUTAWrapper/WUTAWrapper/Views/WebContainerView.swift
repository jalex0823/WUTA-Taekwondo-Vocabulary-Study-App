import SwiftUI

struct WebContainerView: View {
    let url: URL

    @EnvironmentObject private var subscriptionManager: SubscriptionManager

    var body: some View {
        NavigationStack {
            WebView(url: url)
                .navigationTitle("WUTA")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Menu {
                            Button("Restore Purchases") {
                                Task { await subscriptionManager.restorePurchases() }
                            }
                            Button("Refresh Subscription") {
                                Task { await subscriptionManager.refreshEntitlements() }
                            }
                        } label: {
                            Image(systemName: "ellipsis.circle")
                        }
                    }
                }
        }
    }
}
