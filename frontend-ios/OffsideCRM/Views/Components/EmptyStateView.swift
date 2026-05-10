import SwiftUI

struct EmptyStateView: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(spacing: 8) {
            Eyebrow(text: "Nothing here")
            Text(title + ".")
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.brandInk)
            Text(subtitle)
                .font(.callout)
                .foregroundColor(.brandMuted)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(32)
    }
}
