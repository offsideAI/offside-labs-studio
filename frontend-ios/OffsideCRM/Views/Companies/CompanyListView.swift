import SwiftUI

@Observable
final class CompanyListModel {
    var companies: [Company] = []
    var isLoading = false
    var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            let page: Paginated<Company> = try await APIClient.shared.request(
                "GET",
                path: "api/companies/"
            )
            companies = page.results
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? "Could not load companies."
        }
    }
}

struct CompanyListView: View {
    let workspace: Workspace
    @State private var model = CompanyListModel()

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            if model.companies.isEmpty && !model.isLoading {
                EmptyStateView(
                    title: "No companies yet",
                    subtitle: "Add one on app.offside.ai. Companies are the parent record for contacts and deals."
                )
            } else {
                List(model.companies) { company in
                    NavigationLink(value: company) {
                        CompanyRow(company: company)
                    }
                    .listRowBackground(Color.brandBone)
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
                .refreshable { await model.load() }
            }
            if let message = model.errorMessage {
                ErrorBanner(message: message) { Task { await model.load() } }
            }
        }
        .navigationTitle("Companies")
        .navigationDestination(for: Company.self) { company in
            CompanyDetailView(company: company)
        }
        .task { await model.load() }
    }
}

private struct CompanyRow: View {
    let company: Company
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(company.name)
                .font(.body.weight(.medium))
                .foregroundColor(.brandInk)
            HStack(spacing: 8) {
                if !company.domain.isEmpty {
                    Text(company.domain)
                        .font(.caption)
                        .foregroundColor(.brandMuted)
                }
                if !company.sizeBand.isEmpty {
                    StatusPill(label: company.sizeBand)
                }
            }
        }
        .padding(.vertical, 4)
    }
}
