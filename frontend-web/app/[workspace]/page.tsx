"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import * as React from "react";

import {
  AuthFetchError,
  useCreateInvitation,
  useInvitations,
  useMemberships,
  type Membership,
} from "../../lib/api";
import { useActiveWorkspace } from "../../lib/contexts";

export default function WorkspaceHomePage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;

  return (
    <div className="container-editorial section-rhythm space-y-12">
      <header>
        <Eyebrow>Workspace · {active.role ?? "member"}</Eyebrow>
        <h1 className="mt-3 text-5xl font-styrene font-bold tracking-tight md:text-6xl">
          {active.name}<span className="tan-period">.</span>
        </h1>
        <p className="mt-4 text-fg-muted">
          slug: <code>{active.slug}</code> · plan: {active.plan}
        </p>
      </header>

      <Hairline />

      <MembershipsCard workspaceId={active.id} />

      <InvitationsCard workspaceId={active.id} canInvite={canInvite(active.role)} />

      <Hairline />

      <footer className="text-sm text-fg-muted">
        <p>
          Real CRM features (contacts, companies, deals) ship in M4. The{" "}
          <Link href="/brand" className="link-tan">
            brand tokens demo
          </Link>{" "}
          is still live.
        </p>
      </footer>
    </div>
  );
}

const canInvite = (role: string | null) =>
  role === "owner" || role === "admin";

const MembershipsCard = ({ workspaceId }: { workspaceId: number }) => {
  const memberships = useMemberships(workspaceId);
  return (
    <section>
      <Eyebrow>Team</Eyebrow>
      <h2 className="mt-2 text-2xl font-styrene font-bold">Members.</h2>
      <ul className="mt-4 divide-y hairline">
        {memberships.isLoading ? (
          <li className="py-3 text-fg-muted">Loading…</li>
        ) : (
          (memberships.data?.results ?? []).map((m: Membership) => (
            <li key={m.id} className="flex items-center justify-between py-3">
              <div className="space-y-1">
                <p className="font-medium">{m.user_full_name || m.user_email}</p>
                <p className="text-xs text-fg-muted">{m.user_email}</p>
              </div>
              <StatusPill tone="neutral">{m.role}</StatusPill>
            </li>
          ))
        )}
      </ul>
    </section>
  );
};

const InvitationsCard = ({
  workspaceId,
  canInvite,
}: {
  workspaceId: number;
  canInvite: boolean;
}) => {
  const invitations = useInvitations(workspaceId);
  const create = useCreateInvitation(workspaceId);

  const [email, setEmail] = React.useState("");
  const [role, setRole] = React.useState("rep");
  const [error, setError] = React.useState<string | null>(null);
  const [sent, setSent] = React.useState(false);

  if (!canInvite) {
    return (
      <Card>
        <CardHeader>
          <Eyebrow>Invitations</Eyebrow>
          <h3 className="text-xl font-styrene font-bold">Owners and admins can invite teammates.</h3>
        </CardHeader>
      </Card>
    );
  }

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSent(false);
    try {
      await create.mutateAsync({ email, role });
      setEmail("");
      setSent(true);
    } catch (err) {
      if (err instanceof AuthFetchError) {
        setError(`Could not send invitation (${err.status}).`);
      } else {
        setError("Could not send invitation.");
      }
    }
  };

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Invitations</Eyebrow>
        <h3 className="text-xl font-styrene font-bold">Invite a teammate.</h3>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-wrap gap-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="teammate@company.com"
            required
            className="grow rounded-sm border hairline bg-bone px-3 py-2 text-sm"
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="rounded-sm border hairline bg-bone px-3 py-2 text-sm"
          >
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="rep">Rep</option>
            <option value="read_only">Read-only</option>
          </select>
          <button
            type="submit"
            disabled={create.isPending}
            className="rounded-sm border border-ink bg-ink px-4 py-2 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-60"
          >
            {create.isPending ? "Sending…" : "Send invite"}
          </button>
        </form>

        {sent ? <p className="mt-3 text-sm text-fg-muted">Invitation sent.</p> : null}
        {error ? (
          <p role="alert" className="mt-3 text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <ul className="mt-6 space-y-2">
          {(invitations.data?.results ?? []).map((inv) => (
            <li key={inv.id} className="flex items-center justify-between text-sm">
              <span>{inv.email}</span>
              <span className="font-mono text-xs text-fg-muted">
                {inv.role} · {inv.accepted_at ? "accepted" : "pending"}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};
