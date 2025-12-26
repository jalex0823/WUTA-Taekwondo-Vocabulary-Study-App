import Foundation
import StoreKit

@MainActor
final class SubscriptionManager: ObservableObject {
    /// Replace with your App Store Connect product id.
    /// Example: com.yourcompany.wuta.premium.monthly
    static let SUBSCRIPTION_PRODUCT_ID = "YOUR_PRODUCT_ID_HERE"

    @Published var products: [Product] = []
    @Published var isSubscribed: Bool = false
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private var updatesTask: Task<Void, Never>?

    deinit {
        updatesTask?.cancel()
    }

    func initialize() async {
        // Listen for transaction updates (renewals, refunds, etc.)
        updatesTask?.cancel()
        updatesTask = Task { [weak self] in
            for await _ in Transaction.updates {
                await self?.refreshEntitlements()
            }
        }

        await loadProducts()
        await refreshEntitlements()
    }

    func loadProducts() async {
        isLoading = true
        defer { isLoading = false }

        do {
            let ids: Set<String> = [Self.SUBSCRIPTION_PRODUCT_ID]
            let fetched = try await Product.products(for: ids)
            products = fetched
        } catch {
            errorMessage = "Could not load subscription options: \(error.localizedDescription)"
        }
    }

    func refreshEntitlements() async {
        // True if the user currently has an active entitlement for the subscription product.
        var active = false

        for await entitlement in Transaction.currentEntitlements {
            guard case .verified(let transaction) = entitlement else { continue }
            if transaction.productID == Self.SUBSCRIPTION_PRODUCT_ID {
                // For auto-renewable subscriptions, StoreKit keeps current entitlements updated.
                active = true
                break
            }
        }

        isSubscribed = active
    }

    func purchase(product: Product) async {
        isLoading = true
        defer { isLoading = false }

        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                guard case .verified(let transaction) = verification else {
                    errorMessage = "Purchase could not be verified."
                    return
                }

                // Finish the transaction and refresh.
                await transaction.finish()
                await refreshEntitlements()

            case .userCancelled:
                return

            case .pending:
                errorMessage = "Purchase is pending approval."

            @unknown default:
                errorMessage = "Unknown purchase state."
            }
        } catch {
            errorMessage = "Purchase failed: \(error.localizedDescription)"
        }
    }

    func restorePurchases() async {
        isLoading = true
        defer { isLoading = false }

        do {
            try await AppStore.sync()
            await refreshEntitlements()
        } catch {
            errorMessage = "Restore failed: \(error.localizedDescription)"
        }
    }
}
