import Foundation

// URLSession-based client mirroring packages/auth-utils/src/authFetch.ts.
//
// - Bearer auth from KeychainStore
// - X-Workspace-Id header when an active workspace is set
// - Single retry on 401 after refreshing the token
// - JSONDecoder configured for snake_case API → camelCase Swift

enum APIError: Error, LocalizedError {
    case http(status: Int, body: String)
    case transport(Error)
    case decoding(Error)
    case unauthenticated

    var errorDescription: String? {
        switch self {
        case .http(let status, let body): return "HTTP \(status): \(body)"
        case .transport(let err): return "Network: \(err.localizedDescription)"
        case .decoding(let err): return "Decode: \(err.localizedDescription)"
        case .unauthenticated: return "Not signed in."
        }
    }
}

final class APIClient {
    static let shared = APIClient()

    /// Override at app start — defaults to localhost for the simulator.
    /// Production binds to https://crm-api.offside.ai (set in Info.plist as `OffsideApiBaseUrl`).
    var baseURL: URL = {
        if let raw = Bundle.main.object(forInfoDictionaryKey: "OffsideApiBaseUrl") as? String,
           let url = URL(string: raw) {
            return url
        }
        return URL(string: "http://localhost:8000")!
    }()

    var activeWorkspaceID: Int?

    /// Called by AuthStore on a refresh failure so the UI can route to /login.
    var onAuthFailure: (() -> Void)?

    private let session: URLSession = .shared
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    private init() {
        decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    @discardableResult
    func request<T: Decodable>(
        _ method: String,
        path: String,
        body: Encodable? = nil,
        attachWorkspace: Bool = true,
        decodeAs _: T.Type = T.self
    ) async throws -> T {
        let data = try await rawRequest(method, path: path, body: body, attachWorkspace: attachWorkspace)
        if data.isEmpty {
            // 204 No Content; only valid when T is `Empty`.
            if T.self == Empty.self {
                // swiftlint:disable:next force_cast
                return Empty() as! T
            }
        }
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }

    func rawRequest(
        _ method: String,
        path: String,
        body: Encodable? = nil,
        attachWorkspace: Bool = true
    ) async throws -> Data {
        var firstAttempt = try buildRequest(method: method, path: path, body: body, attachWorkspace: attachWorkspace)
        let (data, response) = try await send(firstAttempt)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.transport(URLError(.badServerResponse))
        }

        if http.statusCode == 401, KeychainStore.load() != nil {
            let refreshed = await refreshTokens()
            if refreshed {
                firstAttempt = try buildRequest(method: method, path: path, body: body, attachWorkspace: attachWorkspace)
                let (retryData, retryResp) = try await send(firstAttempt)
                guard let retryHttp = retryResp as? HTTPURLResponse else {
                    throw APIError.transport(URLError(.badServerResponse))
                }
                if retryHttp.statusCode >= 400 {
                    let body = String(data: retryData, encoding: .utf8) ?? ""
                    throw APIError.http(status: retryHttp.statusCode, body: body)
                }
                return retryData
            } else {
                onAuthFailure?()
                throw APIError.unauthenticated
            }
        }

        if http.statusCode >= 400 {
            let body = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http(status: http.statusCode, body: body)
        }
        return data
    }

    private func buildRequest(
        method: String,
        path: String,
        body: Encodable?,
        attachWorkspace: Bool
    ) throws -> URLRequest {
        let url = baseURL.appendingPathComponent(path.hasPrefix("/") ? String(path.dropFirst()) : path)
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Accept")
        if let tokens = KeychainStore.load() {
            req.setValue("Bearer \(tokens.access)", forHTTPHeaderField: "Authorization")
        }
        if attachWorkspace, let wid = activeWorkspaceID {
            req.setValue(String(wid), forHTTPHeaderField: "X-Workspace-Id")
        }
        if let body = body {
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = try encoder.encode(AnyEncodable(body))
        }
        return req
    }

    private func send(_ request: URLRequest) async throws -> (Data, URLResponse) {
        do {
            return try await session.data(for: request)
        } catch {
            throw APIError.transport(error)
        }
    }

    private func refreshTokens() async -> Bool {
        guard let tokens = KeychainStore.load() else { return false }
        let url = baseURL.appendingPathComponent("api/auth/token/refresh/")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? encoder.encode(["refresh": tokens.refresh])
        do {
            let (data, response) = try await session.data(for: req)
            guard let http = response as? HTTPURLResponse, http.statusCode < 400 else {
                KeychainStore.clear()
                return false
            }
            let payload = try decoder.decode(RefreshResponse.self, from: data)
            KeychainStore.save(Tokens(access: payload.access, refresh: payload.refresh ?? tokens.refresh))
            return true
        } catch {
            KeychainStore.clear()
            return false
        }
    }
}

// Type-erased encodable so the API client can take any `Encodable` body
// without exposing generics on every call site.
struct AnyEncodable: Encodable {
    private let encode: (Encoder) throws -> Void
    init(_ wrapped: Encodable) {
        self.encode = wrapped.encode
    }
    func encode(to encoder: Encoder) throws { try encode(encoder) }
}

/// Sentinel for endpoints that return 204 No Content.
struct Empty: Codable {}
