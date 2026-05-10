import SwiftUI

/// Brand eyebrow: UPPERCASE, 0.18em-tracked, tan-text on bone surfaces.
struct Eyebrow: View {
    let text: String
    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 11, weight: .bold))
            .tracking(2.0) // ~0.18em on 11pt
            .foregroundColor(.brandTanText)
    }
}

#Preview {
    Eyebrow(text: "Workspace · Owner")
        .padding()
        .background(Color.brandBone)
}
