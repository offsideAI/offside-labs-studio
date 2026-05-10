"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import { useRouter } from "next/navigation";
import * as React from "react";

import {
  AuthFetchError,
  useArchiveWorkspace,
  useMemberships,
  useUpdateMembershipRole,
  type Membership,
} from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

const ROLES_PROMOTABLE = [
  { value: "admin", label: "Admin" },
  { value: "manager", label: "Manager" },
  { value: "rep", label: "Rep" },
  { value: "read_only", label: "Read-only" },
] as const;

export default function SettingsPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;

  const isOwnerOrAdmin = active.role === "owner" || active.role === "admin";
  const isOwner = active.role === "owner";

  return (
    <div className="container-editorial section-rhythm space-y-12 py-12">
      <header>
        <Eyebrow>Settings</Eyebrow>
        <h1 className="mt-3 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
          {active.name}<span className="tan-period">.</span>
        </h1>
        <p className="mt-3 text-fg-muted">
          slug: <code>{active.slug}</code> · plan: {active.plan} · your role:{" "}
          <strong>{active.role}</strong>
        </p>
      </header>

      <Hairline />

      <TeamSection workspaceId={active.id} canEdit={isOwnerOrAdmin} />

      <Hairline />

      <DangerSection workspaceId={active.id} workspaceSlug={active.slug} canArchive={isOwner} />
    </div>
  );
}

const TeamSection = ({
  workspaceId,
  canEdit,
}: {
  workspaceId: number;
  canEdit: boolean;
}) => {
  const memberships = useMemberships(workspaceId);
  const updateRole = useUpdateMembershipRole(workspaceId);
  const [error, setError] = React.useState<string | null>(null);

  const onChangeRole = async (membershipId: number, role: string) => {
    setError(null);
    try {
      await updateRole.mutateAsync({ membershipId, role });
    } catch (err) {
      if (err instanceof AuthFetchError) {
        const detail =
          (err.payload as { detail?: string })?.detail ?? `Could not update role (${err.status}).`;
        setError(detail);
      } else {
        setError("Could not update role.");
      }
    }
  };

  return (
    <section>
      <Eyebrow>Team</Eyebrow>
      <h2 className="mt-2 text-2xl font-styrene font-bold">Members.</h2>
      {!canEdit ? (
        <p className="mt-2 text-sm text-fg-muted">Owners and admins can change roles.</p>
      ) : null}

      <ul className="mt-6 divide-y hairline">
        {memberships.isLoading ? (
          <li className="py-3 text-fg-muted">Loading…</li>
        ) : (
          (memberships.data?.results ?? []).map((m: Membership) => (
            <li key={m.id} className="flex items-center justify-between gap-4 py-3">
              <div className="space-y-1">
                <p className="font-medium">{m.user_full_name || m.user_email}</p>
                <p className="text-xs text-fg-muted">{m.user_email}</p>
              </div>
              {canEdit && m.role !== "owner" ? (
                <select
                  value={m.role}
                  onChange={(e) => onChangeRole(m.id, e.target.value)}
                  className="rounded-sm border hairline bg-bone px-3 py-1.5 text-sm"
                  aria-label={`Role for ${m.user_email}`}
                >
                  {ROLES_PROMOTABLE.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              ) : (
                <StatusPill tone="neutral">{m.role}</StatusPill>
              )}
            </li>
          ))
        )}
      </ul>

      {error ? (
        <p role="alert" className="mt-3 text-sm text-[#8E3B30]">
          {error}
        </p>
      ) : null}
    </section>
  );
};

const DangerSection = ({
  workspaceId,
  workspaceSlug,
  canArchive,
}: {
  workspaceId: number;
  workspaceSlug: string;
  canArchive: boolean;
}) => {
  const router = useRouter();
  const archive = useArchiveWorkspace(workspaceId);
  const [confirmText, setConfirmText] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  if (!canArchive) {
    return (
      <Card>
        <CardHeader>
          <Eyebrow>Workspace</Eyebrow>
          <h3 className="text-xl font-styrene font-bold">Only the owner can archive.</h3>
        </CardHeader>
      </Card>
    );
  }

  const onArchive = async () => {
    setError(null);
    try {
      await archive.mutateAsync();
      router.replace("/onboarding");
    } catch {
      setError("Could not archive the workspace.");
    }
  };

  const canConfirm = confirmText === workspaceSlug;

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Danger zone</Eyebrow>
        <h3 className="text-xl font-styrene font-bold">Archive this workspace.</h3>
      </CardHeader>
      <CardContent>
        <p className="text-fg-muted">
          Archiving soft-deletes the workspace. Data is retained for 30 days, then hard-deleted.
          To confirm, type the workspace slug <code>{workspaceSlug}</code> below.
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder={workspaceSlug}
            className="rounded-sm border hairline bg-bone px-3 py-2 text-sm"
            aria-label="Confirm workspace slug"
          />
          <button
            type="button"
            onClick={onArchive}
            disabled={!canConfirm || archive.isPending}
            className="rounded-sm border border-[#8E3B30] bg-[#8E3B30] px-4 py-2 text-sm font-bold text-bone hover:bg-[#7a3127] disabled:opacity-40"
          >
            {archive.isPending ? "Archiving…" : "Archive workspace"}
          </button>
        </div>
        {error ? (
          <p role="alert" className="mt-3 text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
};
