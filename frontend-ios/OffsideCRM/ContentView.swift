import SwiftUI

// Brand tokens mirrored from packages/ui/src/styles/tokens.css.
// M6 will refactor these into a typed Color+Brand extension.
private extension Color {
    static let brandTan = Color(red: 201 / 255, green: 163 / 255, blue: 137 / 255) // #C9A389
    static let brandTanText = Color(red: 122 / 255, green: 95 / 255, blue: 68 / 255) // #7A5F44
    static let brandInk = Color(red: 30 / 255, green: 30 / 255, blue: 30 / 255) // #1E1E1E
    static let brandBone = Color(red: 241 / 255, green: 241 / 255, blue: 241 / 255) // #F1F1F1
}

struct ContentView: View {
    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()

            VStack(alignment: .leading, spacing: 16) {
                Text("OFFSIDE STUDIO · PRODUCT 01 · LETTER C")
                    .font(.system(size: 12, weight: .bold))
                    .tracking(2.16) // 0.18em at 12px
                    .foregroundColor(.brandTanText)

                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text("Offside CRM")
                        .font(.system(size: 56, weight: .bold))
                        .foregroundColor(.brandInk)
                    Text(".")
                        .font(.system(size: 56, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                Text("AI-native CRM with deeply integrated workflow automation. M0 scaffold — real chrome ships at M6.")
                    .font(.body)
                    .foregroundColor(Color.brandInk.opacity(0.64))
                    .padding(.top, 8)
                    .lineLimit(nil)
                    .fixedSize(horizontal: false, vertical: true)

                HStack(spacing: 8) {
                    Capsule()
                        .fill(Color.brandTan.opacity(0.2))
                        .frame(width: 6, height: 6)
                    Text("Placeholder · brand parity validated")
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(Color.brandInk.opacity(0.5))
                }
                .padding(.top, 32)

                Spacer()
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        }
    }
}

#Preview {
    ContentView()
}
