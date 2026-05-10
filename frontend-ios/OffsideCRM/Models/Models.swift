import Foundation

// Domain model mirrors. Once OpenAPI Swift codegen is wired, these get
// replaced by generated types. The decoder uses convertFromSnakeCase so
// we can stay with idiomatic Swift property names.

struct User: Codable, Identifiable, Hashable {
    let id: Int
    let email: String
    let fullName: String
    let avatarUrl: String
    let dateJoined: String
}

struct Workspace: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let slug: String
    let plan: String
    let role: String?
}

struct Pipeline: Codable, Identifiable, Hashable {
    struct Stage: Codable, Hashable {
        let id: String
        let label: String
        let order: Int
    }
    let id: Int
    let name: String
    let stages: [Stage]
    let isDefault: Bool
}

struct Contact: Codable, Identifiable, Hashable {
    let id: Int
    let firstName: String
    let lastName: String
    let primaryEmail: String
    let title: String
    let company: Int?
    let owner: Int?
    let lifecycleStage: String
    let source: String
    let createdAt: String

    var displayName: String {
        let combined = "\(firstName) \(lastName)".trimmingCharacters(in: .whitespaces)
        return combined.isEmpty ? primaryEmail : combined
    }
}

struct Company: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let domain: String
    let sizeBand: String
    let industry: String
    let owner: Int?
    let createdAt: String
}

struct Deal: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let pipeline: Int
    let stageId: String
    let valueCents: Int
    let currency: String
    let expectedClose: String?
    let contact: Int?
    let company: Int?
    let owner: Int?
    let createdAt: String

    var formattedValue: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = currency
        formatter.maximumFractionDigits = 0
        return formatter.string(from: NSNumber(value: Double(valueCents) / 100.0))
            ?? "\(currency) \(valueCents / 100)"
    }
}

struct Paginated<T: Codable>: Codable {
    let count: Int
    let next: String?
    let previous: String?
    let results: [T]
}

struct LoginResponse: Codable {
    let access: String
    let refresh: String
    let user: User
}

struct RefreshResponse: Codable {
    let access: String
    let refresh: String?
}
