import SwiftUI

enum PillTone {
    case neutral, success, warning, danger, info

    var background: Color {
        switch self {
        case .neutral: return Color.brandInk.opacity(0.06)
        case .success: return .statusSuccessBg
        case .warning: return .statusWarningBg
        case .danger: return .statusDangerBg
        case .info: return .statusInfoBg
        }
    }

    var foreground: Color {
        switch self {
        case .neutral: return Color.brandInk.opacity(0.7)
        case .success: return .statusSuccessFg
        case .warning: return .statusWarningFg
        case .danger: return .statusDangerFg
        case .info: return .statusInfoFg
        }
    }
}

struct StatusPill: View {
    let label: String
    var tone: PillTone = .neutral

    var body: some View {
        Text(label)
            .font(.system(size: 11, weight: .medium))
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(tone.background, in: Capsule())
            .foregroundColor(tone.foreground)
    }
}
