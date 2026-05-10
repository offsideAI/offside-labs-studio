import SwiftUI

struct MainTabView: View {
    @Bindable var store: AuthStore
    let workspace: Workspace

    var body: some View {
        TabView {
            NavigationStack {
                ContactListView(workspace: workspace)
            }
            .tabItem { Label("Contacts", systemImage: "person.2") }

            NavigationStack {
                CompanyListView(workspace: workspace)
            }
            .tabItem { Label("Companies", systemImage: "building.2") }

            NavigationStack {
                DealListView(workspace: workspace)
            }
            .tabItem { Label("Deals", systemImage: "chart.bar") }

            NavigationStack {
                MoreView(store: store, workspace: workspace)
            }
            .tabItem { Label("More", systemImage: "ellipsis") }
        }
        .tint(.brandTan)
    }
}

private struct MoreView: View {
    @Bindable var store: AuthStore
    let workspace: Workspace

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Account")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text(workspace.name)
                        .font(.system(size: 28, weight: .bold))
                    Text(".")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.brandTan)
                }
                if let user = store.currentUser {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(user.fullName.isEmpty ? user.email : user.fullName)
                            .font(.body.weight(.medium))
                        Text(user.email)
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.brandMuted)
                    }
                }

                if store.workspaces.count > 1 {
                    VStack(alignment: .leading, spacing: 8) {
                        Eyebrow(text: "Switch workspace")
                        ForEach(store.workspaces) { ws in
                            Button {
                                store.selectWorkspace(ws)
                            } label: {
                                HStack {
                                    Text(ws.name)
                                    Spacer()
                                    if ws.id == workspace.id {
                                        Image(systemName: "checkmark").foregroundColor(.brandTan)
                                    }
                                }
                                .padding(.vertical, 8)
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(.brandInk)
                        }
                    }
                    .padding(.top, 8)
                }

                Spacer()

                Button("Sign out", role: .destructive) {
                    store.logout()
                }
                .font(.callout)
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}
