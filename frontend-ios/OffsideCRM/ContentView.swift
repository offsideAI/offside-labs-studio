import SwiftUI

/// Root router. Switches between sign-in, workspace picker, and the
/// authenticated TabView based on AuthStore.state.
struct ContentView: View {
    @State private var auth = AuthStore()

    var body: some View {
        Group {
            switch auth.state {
            case .unknown:
                ProgressView()
                    .tint(.brandTan)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.brandBone.ignoresSafeArea())
            case .signedOut:
                LoginView(store: auth)
            case .needsWorkspace:
                WorkspacePickerView(store: auth)
            case .ready(let workspace):
                MainTabView(store: auth, workspace: workspace)
            }
        }
    }
}

#Preview {
    ContentView()
}
