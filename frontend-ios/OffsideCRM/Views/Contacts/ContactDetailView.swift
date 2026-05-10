import SwiftUI

struct ContactDetailView: View {
    let contact: Contact

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Contact · #\(contact.id)")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text(contact.displayName)
                        .font(.system(size: 32, weight: .bold))
                    Text(".")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                VStack(alignment: .leading, spacing: 12) {
                    DetailRow(label: "Email", value: contact.primaryEmail)
                    DetailRow(label: "Title", value: contact.title)
                    DetailRow(label: "Source", value: contact.source)
                    DetailRow(label: "Lifecycle", value: contact.lifecycleStage)
                }
                .padding(16)
                .background(Color.brandBone)
                .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.brandRule))

                Text("Read-only on iOS today. Editing + tasks/notes/activity feed are M13 work — for now use app.offside.ai.")
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

struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label.uppercased())
                .font(.system(size: 10, weight: .bold))
                .tracking(1.8)
                .foregroundColor(.brandTanText)
            Text(value.isEmpty ? "—" : value)
                .font(.body)
                .foregroundColor(.brandInk)
        }
    }
}
