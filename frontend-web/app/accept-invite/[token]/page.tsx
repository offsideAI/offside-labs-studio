"use client";

import { Eyebrow, StatusPill } from "@offside/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { apiTokens, useAcceptInvitation, usePublicInvitation } from "../../../lib/api";

export default function AcceptInvitePage() {
  const router = useRouter();
  const { token } = useParams<{ token: string }>();
  const invitation = usePublicInvitation(token);
  const accept = useAcceptInvitation();

  const [error, setError] = React.useState<string | null>(null);

  const onAccept = async () => {
    setError(null);
    try {
      const result = await accept.mutateAsync(token);
      router.replace(`/${result.workspace_slug}`);
    } catch (err) {
      setError("Could not accept this invitation. It may have expired or be addressed to a different email.");
    }
  };

  if (invitation.isLoading) {
    return (
      <div className="container-editorial section-rhythm max-w-xl">
        <p className="text-fg-muted">Loading invitation…</p>
      </div>
    );
  }
  if (invitation.isError || !invitation.data) {
    return (
      <div className="container-editorial section-rhythm max-w-xl">
        <Eyebrow>Offside CRM · Invitation</Eyebrow>
        <h1 className="mt-4 text-4xl font-styrene font-bold tracking-tight">
          We can&rsquo;t find that invitation<span className="tan-period">.</span>
        </h1>
        <p className="mt-4 text-fg-muted">
          The link may have been mistyped or the invitation revoked. Ask the workspace owner to
          send a new one.
        </p>
      </div>
    );
  }

  const detail = invitation.data;
  const hasSession = apiTokens.hasSession();

  return (
    <div className="container-editorial section-rhythm max-w-xl space-y-6">
      <Eyebrow>Offside CRM · Invitation</Eyebrow>
      <h1 className="text-4xl font-styrene font-bold tracking-tight">
        Join {detail.workspace_name}<span className="tan-period">.</span>
      </h1>
      <p className="text-fg-muted">
        <strong>{detail.invited_by_email}</strong> invited <strong>{detail.email}</strong> to join{" "}
        <strong>{detail.workspace_name}</strong> as <StatusPill tone="info">{detail.role}</StatusPill>.
      </p>

      {detail.is_expired ? (
        <p role="alert" className="text-sm text-[#8E3B30]">
          This invitation has expired. Ask the inviter to send a new one.
        </p>
      ) : detail.is_accepted ? (
        <p className="text-sm text-fg-muted">This invitation has already been accepted.</p>
      ) : !hasSession ? (
        <div className="space-y-2">
          <p className="text-fg-muted">Sign in or create an account to continue.</p>
          <div className="flex gap-3">
            <Link
              href={`/login?next=/accept-invite/${token}`}
              className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700"
            >
              Sign in
            </Link>
            <Link
              href={`/signup?email=${encodeURIComponent(detail.email)}`}
              className="inline-flex h-10 items-center rounded-sm border border-ink bg-transparent px-4 text-sm font-bold text-ink hover:bg-tan-100"
            >
              Create account
            </Link>
          </div>
        </div>
      ) : (
        <button
          onClick={onAccept}
          disabled={accept.isPending}
          className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-60"
        >
          {accept.isPending ? "Accepting…" : "Accept invitation"}
        </button>
      )}

      {error ? (
        <p role="alert" className="text-sm text-[#8E3B30]">
          {error}
        </p>
      ) : null}
    </div>
  );
}
