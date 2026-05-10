import SwiftUI

@Observable
final class ContactListModel {
    var contacts: [Contact] = []
    var isLoading: Bool = false
    var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            let page: Paginated<Contact> = try await APIClient.shared.request(
                "GET",
                path: "api/contacts/"
            )
            contacts = page.results
        } catch let error as APIError {
            errorMessage = error.localizedDescription
        } catch {
            errorMessage = "Could not load contacts."
        }
    }
}

struct ContactListView: View {
    let workspace: Workspace
    @State private var model = ContactListModel()

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            Group {
                if model.contacts.isEmpty && !model.isLoading {
                    EmptyStateView(
                        title: "No contacts yet",
                        subtitle: "Add one on app.offside.ai or import a CSV. They'll show up here read-only."
                    )
                } else {
                    List(model.contacts) { contact in
                        NavigationLink(value: contact) {
                            ContactRow(contact: contact)
                        }
                        .listRowBackground(Color.brandBone)
                    }
                    .listStyle(.plain)
                    .scrollContentBackground(.hidden)
                    .refreshable { await model.load() }
                }
            }
            if let message = model.errorMessage {
                ErrorBanner(message: message) { Task { await model.load() } }
            }
        }
        .navigationTitle("Contacts")
        .navigationDestination(for: Contact.self) { contact in
            ContactDetailView(contact: contact)
        }
        .task { await model.load() }
    }
}

private struct ContactRow: View {
    let contact: Contact
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(contact.displayName)
                .font(.body.weight(.medium))
                .foregroundColor(.brandInk)
            HStack(spacing: 8) {
                if !contact.primaryEmail.isEmpty {
                    Text(contact.primaryEmail)
                        .font(.caption)
                        .foregroundColor(.brandMuted)
                }
                if !contact.lifecycleStage.isEmpty {
                    StatusPill(label: contact.lifecycleStage)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct ErrorBanner: View {
    let message: String
    let retry: () -> Void
    var body: some View {
        VStack {
            Spacer()
            HStack {
                Text(message)
                    .font(.caption)
                    .foregroundColor(.statusDangerFg)
                    .lineLimit(2)
                Spacer()
                Button("Retry", action: retry)
                    .font(.caption.weight(.bold))
                    .foregroundColor(.brandInk)
            }
            .padding(12)
            .background(Color.statusDangerBg)
            .cornerRadius(6)
            .padding(.horizontal, 16)
            .padding(.bottom, 8)
        }
    }
}
