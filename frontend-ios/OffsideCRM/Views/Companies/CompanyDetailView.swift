import SwiftUI

struct CompanyDetailView: View {
    let company: Company

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Company · #\(company.id)")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text(company.name)
                        .font(.system(size: 32, weight: .bold))
                    Text(".")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                VStack(alignment: .leading, spacing: 12) {
                    DetailRow(label: "Domain", value: company.domain)
                    DetailRow(label: "Industry", value: company.industry)
                    DetailRow(label: "Size", value: company.sizeBand)
                }
                .padding(16)
                .background(Color.brandBone)
                .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.brandRule))

                Text("Linked contacts + deals appear here in M13.")
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
