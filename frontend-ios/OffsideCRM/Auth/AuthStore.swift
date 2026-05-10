import Foundation
import Observation

// Single source of truth for sign-in state + active workspace, observable
// by SwiftUI views via the `@Observable` macro (iOS 17+).

@Observable
final class AuthStore {
    enum State {
        case unknown
        case signedOut
        case needsWorkspace
        case ready(Workspace)
    }

    var state: State = .unknown
    var currentUser: User?
    var workspaces: [Workspace] = []
    var errorMessage: String?

    init() {
        APIClient.shared.onAuthFailure = { [weak self] in
            DispatchQueue.main.async {
                self?.handleAuthFailure()
            }
        }
        bootstrap()
    }

    func bootstrap() {
        guard KeychainStore.load() != nil else {
            state = .signedOut
            return
        }
        Task { await loadSession() }
    }

    func login(email: String, password: String) async {
        errorMessage = nil
        do {
            struct Body: Encodable {
                let email: String
                let password: String
            }
            let response: LoginResponse = try await APIClient.shared.request(
                "POST",
                path: "api/auth/login/",
                body: Body(email: email, password: password),
                attachWorkspace: false
            )
            KeychainStore.save(Tokens(access: response.access, refresh: response.refresh))
            currentUser = response.user
            await loadSession()
        } catch let error as APIError {
            errorMessage = "Sign in failed."
            print("[Auth] login failed:", error.localizedDescription)
        } catch {
            errorMessage = "Sign in failed."
        }
    }

    func loadSession() async {
        do {
            currentUser = try await APIClient.shared.request(
                "GET",
                path: "api/auth/user/",
                attachWorkspace: false
            )
            let page: Paginated<Workspace> = try await APIClient.shared.request(
                "GET",
                path: "api/workspaces/",
                attachWorkspace: false
            )
            workspaces = page.results
            if let first = workspaces.first {
                APIClient.shared.activeWorkspaceID = first.id
                state = .ready(first)
            } else {
                state = .needsWorkspace
            }
        } catch {
            handleAuthFailure()
        }
    }

    func selectWorkspace(_ workspace: Workspace) {
        APIClient.shared.activeWorkspaceID = workspace.id
        state = .ready(workspace)
    }

    func logout() {
        KeychainStore.clear()
        APIClient.shared.activeWorkspaceID = nil
        currentUser = nil
        workspaces = []
        state = .signedOut
    }

    private func handleAuthFailure() {
        KeychainStore.clear()
        APIClient.shared.activeWorkspaceID = nil
        currentUser = nil
        workspaces = []
        state = .signedOut
    }
}
