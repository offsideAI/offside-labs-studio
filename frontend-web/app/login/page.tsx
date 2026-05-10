"use client";

import { Eyebrow } from "@offside/ui";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";

import { useLogin, useWorkspaces } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next");

  const login = useLogin();
  const workspaces = useWorkspaces();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await login.mutateAsync({ email, password });
      const list = await workspaces.refetch();
      const first = list.data?.results[0];
      if (next) {
        router.replace(next);
      } else if (first) {
        router.replace(`/${first.slug}`);
      } else {
        router.replace("/onboarding");
      }
    } catch (err) {
      setError("Email or password didn't match.");
    }
  };

  return (
    <div className="container-editorial section-rhythm max-w-md">
      <Eyebrow>Offside CRM · Sign in</Eyebrow>
      <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
        Welcome back<span className="tan-period">.</span>
      </h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Field label="Email" htmlFor="email">
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </Field>
        <Field label="Password" htmlFor="password">
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            minLength={10}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
          />
        </Field>

        {error ? (
          <p role="alert" className="text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={login.isPending}
          className="button-primary w-full"
        >
          {login.isPending ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="mt-8 text-sm text-fg-muted">
        New to Offside?{" "}
        <Link href="/signup" className="link-tan">
          Create an account
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
