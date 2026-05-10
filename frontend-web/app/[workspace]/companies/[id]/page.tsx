"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import {
  useCompany,
  useContacts,
  useDeleteCompany,
  useUpdateCompany,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { CustomFieldsPanel } from "../../../../components/custom-fields-panel";

const SIZE_BANDS = ["", "1-10", "11-50", "51-200", "201-1000", "1000+"];

export default function CompanyDetailPage() {
  const params = useParams<{ workspace: string; id: string }>();
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return (
    <CompanyDetail workspaceId={active.id} workspaceSlug={params.workspace} companyId={params.id} />
  );
}

const CompanyDetail = ({
  workspaceId,
  workspaceSlug,
  companyId,
}: {
  workspaceId: number;
  workspaceSlug: string;
  companyId: string;
}) => {
  const router = useRouter();
  const company = useCompany(workspaceId, companyId);
  const update = useUpdateCompany(workspaceId);
  const remove = useDeleteCompany(workspaceId);
  const contacts = useContacts(workspaceId, {
    field: "company",
    op: "eq",
    value: Number(companyId),
  });

  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState<Record<string, unknown>>({});

  React.useEffect(() => {
    if (!company.data) return;
    setDraft({
      name: company.data.name,
      domain: company.data.domain,
      industry: company.data.industry,
      size_band: company.data.size_band,
      custom: company.data.custom,
    });
  }, [company.data]);

  if (company.isLoading || !company.data) {
    return (
      <div className="container-editorial section-rhythm py-12">
        <p className="text-fg-muted">Loading company…</p>
      </div>
    );
  }

  const c = company.data;

  const onSave = async () => {
    await update.mutateAsync({ id: c.id, patch: draft });
    setEditing(false);
  };

  const onArchive = async () => {
    if (!window.confirm("Archive this company? Contacts stay; the company is hidden.")) return;
    await remove.mutateAsync(c.id);
    router.replace(`/${workspaceSlug}/companies`);
  };

  const inputClass =
    "w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2";

  return (
    <div className="container-editorial section-rhythm space-y-10 py-12">
      <div>
        <Link href={`/${workspaceSlug}/companies`} className="link-tan text-sm">
          ← Companies
        </Link>
      </div>

      <header className="flex items-start justify-between gap-4">
        <div>
          <Eyebrow>Company · #{c.id}</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            {c.name}<span className="tan-period">.</span>
          </h1>
          <p className="mt-2 text-fg-muted">
            {c.domain || "no domain"} · created {new Date(c.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          {editing ? (
            <>
              <button onClick={onSave} disabled={update.isPending} className="button-primary">
                {update.isPending ? "Saving…" : "Save"}
              </button>
              <button
                onClick={() => setEditing(false)}
                className="rounded-sm border hairline bg-bone px-4 py-2 text-sm font-medium hover:bg-tan-100"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button onClick={() => setEditing(true)} className="button-primary">
                Edit
              </button>
              <button
                onClick={onArchive}
                disabled={remove.isPending}
                className="rounded-sm border border-[#8E3B30] bg-transparent px-4 py-2 text-sm font-medium text-[#8E3B30] hover:bg-[#F4DEDA]"
              >
                Archive
              </button>
            </>
          )}
        </div>
      </header>

      <Hairline />

      <Card>
        <CardHeader>
          <Eyebrow>Details</Eyebrow>
          <h2 className="text-xl font-styrene font-bold">Standard fields.</h2>
        </CardHeader>
        <CardContent>
          {editing ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field label="Name">
                <input
                  value={(draft.name as string) ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
                  className={inputClass}
                />
              </Field>
              <Field label="Domain">
                <input
                  value={(draft.domain as string) ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, domain: e.target.value }))}
                  className={inputClass}
                />
              </Field>
              <Field label="Industry">
                <input
                  value={(draft.industry as string) ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, industry: e.target.value }))}
                  className={inputClass}
                />
              </Field>
              <Field label="Size band">
                <select
                  value={(draft.size_band as string) ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, size_band: e.target.value }))}
                  className={inputClass}
                >
                  {SIZE_BANDS.map((s) => (
                    <option key={s} value={s}>
                      {s || "—"}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
          ) : (
            <dl className="grid grid-cols-1 gap-x-8 gap-y-3 md:grid-cols-2">
              <Pair label="Name" value={c.name} />
              <Pair label="Domain" value={c.domain} />
              <Pair label="Industry" value={c.industry} />
              <Pair
                label="Size band"
                value={
                  c.size_band ? <StatusPill tone="neutral">{c.size_band}</StatusPill> : "—"
                }
              />
            </dl>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Eyebrow>Custom fields</Eyebrow>
          <h2 className="text-xl font-styrene font-bold">Workspace-specific.</h2>
        </CardHeader>
        <CardContent>
          <CustomFieldsPanel
            workspaceId={workspaceId}
            entityType="company"
            values={(editing ? (draft.custom as Record<string, unknown>) : c.custom) ?? {}}
            onChange={(next) => setDraft((d) => ({ ...d, custom: next }))}
            disabled={!editing}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Eyebrow>Contacts ({contacts.data?.count ?? 0})</Eyebrow>
          <h2 className="text-xl font-styrene font-bold">People at {c.name}.</h2>
        </CardHeader>
        <CardContent>
          {(contacts.data?.results ?? []).length === 0 ? (
            <p className="text-fg-muted">No contacts linked yet.</p>
          ) : (
            <ul className="divide-y hairline">
              {(contacts.data?.results ?? []).map((contact) => (
                <li key={contact.id} className="flex items-center justify-between py-2">
                  <Link
                    href={`/${workspaceSlug}/contacts/${contact.id}`}
                    className="font-medium hover:text-tan-text"
                  >
                    {`${contact.first_name} ${contact.last_name}`.trim() ||
                      contact.primary_email}
                  </Link>
                  <span className="text-xs text-fg-muted">{contact.title || "—"}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <style jsx>{`
        .button-primary {
          background: var(--brand-ink);
          color: var(--brand-bone);
          border: 1px solid var(--brand-ink);
          border-radius: 4px;
          padding: 0.5rem 1.25rem;
          font-weight: 700;
          font-size: 0.875rem;
          cursor: pointer;
        }
        .button-primary:hover { background: #303030; }
        .button-primary:disabled { opacity: 0.6; cursor: not-allowed; }
      `}</style>
    </div>
  );
};

const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium">{label}</label>
    {children}
  </div>
);

const Pair = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div>
    <dt className="text-xs font-mono uppercase tracking-eyebrow text-tan-text">{label}</dt>
    <dd className="mt-0.5 text-sm">{value || "—"}</dd>
  </div>
);
