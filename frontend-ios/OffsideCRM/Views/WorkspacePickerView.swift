import SwiftUI

struct WorkspacePickerView: View {
    @Bindable var store: AuthStore

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Pick a workspace")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text("Where to today")
                        .font(.system(size: 32, weight: .bold))
                    Text(".")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                if store.workspaces.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("No workspaces on this account.")
                            .foregroundColor(.brandMuted)
                        Text("Create one on app.offside.ai, or accept a teammate's invitation.")
                            .font(.callout)
                            .foregroundColor(.brandMuted)
                    }
                } else {
                    VStack(spacing: 8) {
                        ForEach(store.workspaces) { workspace in
                            Button {
                                store.selectWorkspace(workspace)
                            } label: {
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(workspace.name).font(.body.weight(.medium))
                                        Text(workspace.slug)
                                            .font(.system(size: 11, design: .monospaced))
                                            .foregroundColor(.brandMuted)
                                    }
                                    Spacer()
                                    if let role = workspace.role {
                                        StatusPill(label: role)
                                    }
                                }
                                .padding(14)
                                .background(Color.brandBone)
                                .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.brandRule))
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(.brandInk)
                        }
                    }
                }

                Spacer()

                Button("Sign out", role: .destructive) {
                    store.logout()
                }
                .font(.callout)
                .padding(.top, 16)
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .topLeading)
        }
    }
}
