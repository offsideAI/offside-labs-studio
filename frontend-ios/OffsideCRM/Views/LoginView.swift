import SwiftUI

struct LoginView: View {
    @Bindable var store: AuthStore
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isSubmitting = false

    var body: some View {
        ZStack {
            Color.brandBone.ignoresSafeArea()
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow(text: "Offside CRM · Sign in")
                HStack(alignment: .firstTextBaseline, spacing: 0) {
                    Text("Welcome back")
                        .font(.system(size: 40, weight: .bold))
                    Text(".")
                        .font(.system(size: 40, weight: .bold))
                        .foregroundColor(.brandTan)
                }

                VStack(alignment: .leading, spacing: 16) {
                    fieldLabel("Email")
                    TextField("you@company.com", text: $email)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .padding(12)
                        .background(Color.brandBone)
                        .overlay(RoundedRectangle(cornerRadius: 4).stroke(Color.brandRule))
                        .accessibilityLabel("Email")

                    fieldLabel("Password")
                    SecureField("••••••••••", text: $password)
                        .textContentType(.password)
                        .padding(12)
                        .background(Color.brandBone)
                        .overlay(RoundedRectangle(cornerRadius: 4).stroke(Color.brandRule))
                        .accessibilityLabel("Password")
                }

                if let message = store.errorMessage {
                    Text(message)
                        .font(.footnote)
                        .foregroundColor(.statusDangerFg)
                }

                Button {
                    Task {
                        isSubmitting = true
                        await store.login(email: email, password: password)
                        isSubmitting = false
                    }
                } label: {
                    HStack {
                        if isSubmitting {
                            ProgressView().tint(.brandBone)
                        }
                        Text(isSubmitting ? "Signing in…" : "Sign in")
                            .font(.system(size: 15, weight: .bold))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color.brandInk)
                    .foregroundColor(.brandBone)
                    .cornerRadius(4)
                }
                .disabled(email.isEmpty || password.isEmpty || isSubmitting)

                Text("This is the iOS shell — signup + workspace creation happens on app.offside.ai today.")
                    .font(.caption)
                    .foregroundColor(.brandMuted)
                    .padding(.top, 8)

                Spacer()
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        }
    }

    @ViewBuilder
    private func fieldLabel(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 13, weight: .medium))
            .foregroundColor(.brandInk)
    }
}
