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
      <Eyebrow>OffsideStudio · Sign in</Eyebrow>
      <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
        Welcome back<span className="tan-period">.</span>
      </h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Field label="Email" htmlFor="email">
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="your@email.com"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-2.5 bg-[#0a0a0a] border border-gray-800 rounded-sm text-white placeholder-gray-600 focus:outline-none focus:border-render-purple transition-colors text-sm"
          />
        </Field>
        <Field label="Password" htmlFor="password">
          <div className="relative">
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="correct horse battery staple"
              required
              minLength={10}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2.5 bg-[#0a0a0a] border border-gray-800 rounded-sm text-white placeholder-gray-600 focus:outline-none focus:border-render-purple transition-colors text-sm pr-10"
            />
            <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </button>
          </div>
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
    <label htmlFor={htmlFor} className="block text-xs font-medium text-gray-300">
      {label}
    </label>
    {children}
  </div>
);
