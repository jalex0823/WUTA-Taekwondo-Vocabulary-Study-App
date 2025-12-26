import SwiftUI
import StoreKit

struct PaywallView: View {
    @EnvironmentObject private var subscriptionManager: SubscriptionManager

    var body: some View {
        VStack(spacing: 16) {
            Spacer()

            Text("WUTA Premium")
                .font(.largeTitle.bold())

            Text("Start your 7-day free trial, then $0.99 per period.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal)

            if subscriptionManager.products.isEmpty {
                Button("Load Options") {
                    Task { await subscriptionManager.loadProducts() }
                }
                .buttonStyle(.borderedProminent)
            } else {
                ForEach(subscriptionManager.products, id: \.id) { product in
                    Button {
                        Task { await subscriptionManager.purchase(product: product) }
                    } label: {
                        VStack(spacing: 6) {
                            Text(product.displayName)
                                .font(.headline)
                            Text(product.displayPrice)
                                .foregroundStyle(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .padding(.horizontal)
                }
            }

            Button("Restore Purchases") {
                Task { await subscriptionManager.restorePurchases() }
            }
            .buttonStyle(.bordered)

            VStack(spacing: 8) {
                Text("By subscribing, you agree to the Terms and Privacy Policy.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)

                // Replace these with your real URLs.
                Link("Privacy Policy", destination: URL(string: "https://YOUR-DOMAIN-HERE.example/privacy")!)
                Link("Terms", destination: URL(string: "https://YOUR-DOMAIN-HERE.example/terms")!)
            }
            .padding(.top, 6)

            Spacer()
        }
        .padding()
        .task {
            if subscriptionManager.products.isEmpty {
                await subscriptionManager.loadProducts()
            }
        }
    }
}
