import SwiftUI

struct DealDetailView: View {
    let deal: Deal
    let stageLabel: String

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Deal · #\(deal.id)")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text(deal.name)
                        .font(.system(size: 32, weight: .bold))
                    Text(".")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                HStack(spacing: 8) {
                    StatusPill(label: stageLabel, tone: .info)
                    Text(deal.formattedValue)
                        .font(.callout.weight(.bold).monospaced())
                        .foregroundColor(.brandTanText)
                }

                VStack(alignment: .leading, spacing: 12) {
                    DetailRow(label: "Currency", value: deal.currency)
                    DetailRow(label: "Expected close", value: deal.expectedClose ?? "—")
                    DetailRow(label: "Created", value: deal.createdAt)
                }
                .padding(16)
                .background(Color.brandBone)
                .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.brandRule))

                Text("Drag-drop stage moves + tasks/notes/activity ship in M13. The web kanban is the system of record today.")
                    .font(.caption)
                    .foregroundColor(.brandMuted)

                Spacer()
            }
            .padding(20)
        }
        .background(Color.brandBone)
        .navigationBarTitleDisplayMode(.inline)
    }
}
