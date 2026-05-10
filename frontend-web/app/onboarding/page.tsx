"use client";

import { Eyebrow } from "@offside/ui";
import { useRouter } from "next/navigation";
import * as React from "react";

import { useCreateWorkspace } from "../../lib/api";
import { AuthGate } from "../../lib/contexts";

export default function OnboardingPage() {
  return (
    <AuthGate>
      <OnboardingForm />
    </AuthGate>
  );
}

const OnboardingForm = () => {
  const router = useRouter();
  const create = useCreateWorkspace();

  const [name, setName] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const workspace = await create.mutateAsync({ name });
      router.replace(`/${workspace.slug}`);
    } catch {
      setError("Couldn't create the workspace. Try a different name.");
    }
  };

  return (
    <div className="container-editorial section-rhythm max-w-xl">
      <Eyebrow>Offside CRM · Set up your workspace</Eyebrow>
      <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
        One last step<span className="tan-period">.</span>
      </h1>
      <p className="mt-6 text-fg-muted">
        A workspace holds your team&rsquo;s contacts, deals, and automations. You can rename it
        later from settings.
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="name" className="text-sm font-medium">
            Workspace name
          </label>
          <input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Acme Sales"
            required
            minLength={2}
            maxLength={120}
            className="input"
          />
          <p className="text-xs text-fg-muted">
            We&rsquo;ll generate a URL slug from this. You can change it later.
          </p>
        </div>

        {error ? (
          <p role="alert" className="text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <button type="submit" disabled={create.isPending} className="button-primary">
          {create.isPending ? "Creating…" : "Create workspace"}
        </button>
      </form>

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
          padding: 0.75rem 1.5rem;
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
};
