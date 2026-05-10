import SwiftUI

@Observable
final class DealListModel {
    var deals: [Deal] = []
    var pipelinesById: [Int: Pipeline] = [:]
    var isLoading = false
    var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            async let dealsPage: Paginated<Deal> = APIClient.shared.request(
                "GET",
                path: "api/deals/"
            )
            async let pipelinesPage: Paginated<Pipeline> = APIClient.shared.request(
                "GET",
                path: "api/pipelines/"
            )
            let (dealsResult, pipelinesResult) = try await (dealsPage, pipelinesPage)
            deals = dealsResult.results
            pipelinesById = Dictionary(uniqueKeysWithValues: pipelinesResult.results.map { ($0.id, $0) })
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? "Could not load deals."
        }
    }

    func stageLabel(for deal: Deal) -> String {
        guard let pipeline = pipelinesById[deal.pipeline] else { return deal.stageId }
        return pipeline.stages.first { $0.id == deal.stageId }?.label ?? deal.stageId
    }
}

struct DealListView: View {
    let workspace: Workspace
    @State private var model = DealListModel()

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            if model.deals.isEmpty && !model.isLoading {
                EmptyStateView(
                    title: "No deals yet",
                    subtitle: "Create deals on app.offside.ai. Drag-and-drop kanban is on the web; iOS list view here."
                )
            } else {
                List(model.deals) { deal in
                    NavigationLink(value: deal) {
                        DealRow(deal: deal, stageLabel: model.stageLabel(for: deal))
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
        .navigationTitle("Deals")
        .navigationDestination(for: Deal.self) { deal in
            DealDetailView(deal: deal, stageLabel: model.stageLabel(for: deal))
        }
        .task { await model.load() }
    }
}

private struct DealRow: View {
    let deal: Deal
    let stageLabel: String
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(deal.name)
                    .font(.body.weight(.medium))
                    .foregroundColor(.brandInk)
                Spacer()
                Text(deal.formattedValue)
                    .font(.caption.weight(.bold).monospaced())
                    .foregroundColor(.brandTanText)
            }
            HStack(spacing: 8) {
                StatusPill(label: stageLabel, tone: stageTone)
                if let close = deal.expectedClose, !close.isEmpty {
                    Text("close \(close)")
                        .font(.caption)
                        .foregroundColor(.brandMuted)
                }
            }
        }
        .padding(.vertical, 4)
    }

    private var stageTone: PillTone {
        switch deal.stageId {
        case "closed_won", "won": return .success
        case "closed_lost", "lost": return .danger
        case "negotiation": return .warning
        default: return .info
        }
    }
}
