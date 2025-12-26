import SwiftUI

struct RootView: View {
    let baseURL: URL

    @EnvironmentObject private var subscriptionManager: SubscriptionManager

    var body: some View {
        Group {
            if subscriptionManager.isSubscribed {
                WebContainerView(url: baseURL)
            } else {
                PaywallView()
            }
        }
        .overlay(alignment: .top) {
            if subscriptionManager.isLoading {
                ProgressView()
                    .padding(12)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .padding(.top, 10)
            }
        }
        .alert("Subscription", isPresented: Binding(get: {
            subscriptionManager.errorMessage != nil
        }, set: { newValue in
            if !newValue { subscriptionManager.errorMessage = nil }
        })) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(subscriptionManager.errorMessage ?? "")
        }
    }
}
