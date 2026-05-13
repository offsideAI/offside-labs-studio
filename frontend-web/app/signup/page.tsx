"use client";

import { Eyebrow } from "@offside/ui";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import { AuthFetchError, useSignup } from "../../lib/api";

export default function SignupPage() {
  const router = useRouter();
  const signup = useSignup();

  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [done, setDone] = React.useState(false);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await signup.mutateAsync({
        email,
        password1: password,
        password2: password,
        full_name: fullName,
      });
      setDone(true);
    } catch (err) {
      if (err instanceof AuthFetchError && typeof err.payload === "object" && err.payload) {
        const flat = Object.entries(err.payload as Record<string, unknown>)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : String(v)}`)
          .join(" — ");
        setError(flat || "Signup failed.");
      } else {
        setError("Signup failed.");
      }
    }
  };

  if (done) {
    return (
      <div className="container-editorial section-rhythm max-w-md">
        <Eyebrow>OffsideStudio · Verify your email</Eyebrow>
        <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
          Check your inbox<span className="tan-period">.</span>
        </h1>
        <p className="mt-6 text-fg-muted">
          We sent a verification link to <strong>{email}</strong>. Click it and you&rsquo;ll be
          able to sign in. The link expires in an hour.
        </p>
        <p className="mt-8 text-sm text-fg-muted">
          <Link href="/login" className="link-tan">
            Back to sign in
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="container-editorial section-rhythm max-w-md">
      <Eyebrow>OffsideStudio · Create account</Eyebrow>
      <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
        Start free<span className="tan-period">.</span>
      </h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Field label="Full name" htmlFor="full_name">
          <input
            id="full_name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            autoComplete="name"
            className="input"
            required
          />
        </Field>
        <Field label="Email" htmlFor="email">
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            className="input"
            required
          />
        </Field>
        <Field label="Password" htmlFor="password">
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={10}
            className="input"
            required
          />
          <p className="text-xs text-fg-muted">10+ characters, mixed case + a digit.</p>
        </Field>

        {error ? (
          <p role="alert" className="text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <button type="submit" disabled={signup.isPending} className="button-primary w-full">
          {signup.isPending ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="mt-8 text-sm text-fg-muted">
        Already have an account?{" "}
        <Link href="/login" className="link-tan">
          Sign in
        </Link>
        .
      </p>

      <style jsx>{`
        .input {
          width: 100%;
          padding: 0.625rem 0.75rem;
          background: var(--brand-bone);
          border: 1px solid var(--brand-rule);
          border-radius: 4px;
          color: var(--brand-ink);
          font-family: var(--font-roboto), system-ui, sans-serif;
          font-size: 0.95rem;
        }
        .input:focus-visible {
          outline: 2px solid var(--brand-tan);
          outline-offset: 2px;
        }
        .button-primary {
          background: var(--brand-ink);
          color: var(--brand-bone);
          border: 1px solid var(--brand-ink);
          border-radius: 4px;
          padding: 0.75rem 1.25rem;
          font-weight: 700;
          font-family: var(--font-roboto), system-ui, sans-serif;
          cursor: pointer;
          transition: background 200ms;
        }
        .button-primary:hover {
          background: #303030;
        }
        .button-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

const Field = ({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) => (
  <div className="space-y-1.5">
    <label htmlFor={htmlFor} className="text-sm font-medium">
      {label}
    </label>
    {children}
  </div>
);
