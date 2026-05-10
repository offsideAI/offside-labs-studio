import SwiftUI

// Brand tokens mirror packages/ui/src/styles/tokens.css. When the OffsideAI
// design system updates, update these in lock-step with the web tokens.

extension Color {
    static let brandTan = Color(red: 201 / 255, green: 163 / 255, blue: 137 / 255)         // #C9A389
    static let brandTanText = Color(red: 122 / 255, green: 95 / 255, blue: 68 / 255)        // #7A5F44 (WCAG-safe on bone)
    static let brandInk = Color(red: 30 / 255, green: 30 / 255, blue: 30 / 255)             // #1E1E1E
    static let brandBone = Color(red: 241 / 255, green: 241 / 255, blue: 241 / 255)         // #F1F1F1
    static let brandRule = Color.brandInk.opacity(0.12)
    static let brandMuted = Color.brandInk.opacity(0.64)

    // Status tones (mirror StatusPill in @offside/ui).
    static let statusSuccessBg = Color(red: 232 / 255, green: 241 / 255, blue: 234 / 255)
    static let statusSuccessFg = Color(red: 59 / 255, green: 106 / 255, blue: 74 / 255)
    static let statusWarningBg = Color(red: 247 / 255, green: 236 / 255, blue: 221 / 255)
    static let statusWarningFg = Color(red: 140 / 255, green: 90 / 255, blue: 31 / 255)
    static let statusDangerBg = Color(red: 244 / 255, green: 222 / 255, blue: 218 / 255)
    static let statusDangerFg = Color(red: 142 / 255, green: 59 / 255, blue: 48 / 255)
    static let statusInfoBg = Color(red: 234 / 255, green: 234 / 255, blue: 236 / 255)
    static let statusInfoFg = Color(red: 61 / 255, green: 63 / 255, blue: 71 / 255)
}
