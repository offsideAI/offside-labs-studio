"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import {
  useCompanies,
  useCompany,
  useContact,
  useDeleteContact,
  useUpdateContact,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { CustomFieldsPanel } from "../../../../components/custom-fields-panel";

const STAGE_OPTIONS = ["", "lead", "qualified", "customer", "churned"];

export default function ContactDetailPage() {
  const params = useParams<{ workspace: string; id: string }>();
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <ContactDetail workspaceId={active.id} workspaceSlug={params.workspace} contactId={params.id} />;
}

const ContactDetail = ({
  workspaceId,
  workspaceSlug,
  contactId,
}: {
  workspaceId: number;
  workspaceSlug: string;
  contactId: string;
}) => {
  const router = useRouter();
  const contact = useContact(workspaceId, contactId);
  const update = useUpdateContact(workspaceId);
  const remove = useDeleteContact(workspaceId);
  const companies = useCompanies(workspaceId);
  const company = useCompany(workspaceId, contact.data?.company ?? "");

  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState<Record<string, unknown>>({});

  React.useEffect(() => {
    if (!contact.data) return;
    setDraft({
      first_name: contact.data.first_name,
      last_name: contact.data.last_name,
      primary_email: contact.data.primary_email,
      title: contact.data.title,
      company: contact.data.company,
      lifecycle_stage: contact.data.lifecycle_stage,
      custom: contact.data.custom,
    });
  }, [contact.data]);

  if (contact.isLoading || !contact.data) {
    return (
      <div className="container-editorial section-rhythm py-12">
        <p className="text-fg-muted">Loading contact…</p>
      </div>
    );
  }

  const c = contact.data;
  const fullName = `${c.first_name} ${c.last_name}`.trim() || c.primary_email || `Contact #${c.id}`;

  const onSave = async () => {
    await update.mutateAsync({ id: c.id, patch: draft });
    setEditing(false);
  };

  const onArchive = async () => {
    if (!window.confirm("Archive this contact? They'll be hidden but recoverable for 90 days.")) return;
    await remove.mutateAsync(c.id);
    router.replace(`/${workspaceSlug}/contacts`);
  };

  return (
    <div className="container-editorial section-rhythm space-y-10 py-12">
      <div>
        <Link href={`/${workspaceSlug}/contacts`} className="link-tan text-sm">
          ← Contacts
        </Link>
      </div>

      <header className="flex items-start justify-between gap-4">
        <div>
          <Eyebrow>Contact · #{c.id}</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            {fullName}<span className="tan-period">.</span>
          </h1>
          <p className="mt-2 text-fg-muted">
            {c.primary_email || "no email on file"} · created{" "}
            {new Date(c.created_at).toLocaleDateString()}
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
            <EditableFields
              draft={draft}
              setDraft={setDraft}
              companies={companies.data?.results ?? []}
            />
          ) : (
            <ReadOnlyFields contact={c} companyName={company.data?.name ?? null} />
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
            entityType="contact"
            values={(editing ? (draft.custom as Record<string, unknown>) : c.custom) ?? {}}
            onChange={(next) => setDraft((d) => ({ ...d, custom: next }))}
            disabled={!editing}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Eyebrow>Activity</Eyebrow>
          <h2 className="text-xl font-styrene font-bold">Coming in M5.</h2>
        </CardHeader>
        <CardContent>
          <p className="text-fg-muted">
            Append-only activity feed (emails / calls / meetings / AI actions / automation runs)
            ships with the deals + tasks milestone.
          </p>
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

const ReadOnlyFields = ({
  contact,
  companyName,
}: {
  contact: import("../../../../lib/api").Contact;
  companyName: string | null;
}) => (
  <dl className="grid grid-cols-1 gap-x-8 gap-y-3 md:grid-cols-2">
    <Pair label="First name" value={contact.first_name} />
    <Pair label="Last name" value={contact.last_name} />
    <Pair label="Email" value={contact.primary_email} />
    <Pair label="Title" value={contact.title} />
    <Pair label="Company" value={companyName ?? "—"} />
    <Pair
      label="Lifecycle stage"
      value={
        contact.lifecycle_stage ? (
          <StatusPill tone="neutral">{contact.lifecycle_stage}</StatusPill>
        ) : (
          "—"
        )
      }
    />
  </dl>
);

const Pair = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div>
    <dt className="text-xs font-mono uppercase tracking-eyebrow text-tan-text">{label}</dt>
    <dd className="mt-0.5 text-sm">{value || "—"}</dd>
  </div>
);

const EditableFields = ({
  draft,
  setDraft,
  companies,
}: {
  draft: Record<string, unknown>;
  setDraft: React.Dispatch<React.SetStateAction<Record<string, unknown>>>;
  companies: Array<{ id: number; name: string }>;
}) => {
  const set = (key: string, value: unknown) => setDraft((d) => ({ ...d, [key]: value }));
  const inputClass =
    "w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2";

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Field label="First name">
        <input
          value={(draft.first_name as string) ?? ""}
          onChange={(e) => set("first_name", e.target.value)}
          className={inputClass}
        />
      </Field>
      <Field label="Last name">
        <input
          value={(draft.last_name as string) ?? ""}
          onChange={(e) => set("last_name", e.target.value)}
          className={inputClass}
        />
      </Field>
      <Field label="Email">
        <input
          type="email"
          value={(draft.primary_email as string) ?? ""}
          onChange={(e) => set("primary_email", e.target.value)}
          className={inputClass}
        />
      </Field>
      <Field label="Title">
        <input
          value={(draft.title as string) ?? ""}
          onChange={(e) => set("title", e.target.value)}
          className={inputClass}
        />
      </Field>
      <Field label="Company">
        <select
          value={(draft.company as number | "") ?? ""}
          onChange={(e) => set("company", e.target.value ? Number(e.target.value) : null)}
          className={inputClass}
        >
          <option value="">—</option>
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Lifecycle stage">
        <select
          value={(draft.lifecycle_stage as string) ?? ""}
          onChange={(e) => set("lifecycle_stage", e.target.value)}
          className={inputClass}
        >
          {STAGE_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s || "—"}
            </option>
          ))}
        </select>
      </Field>
    </div>
  );
};

const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium">{label}</label>
    {children}
  </div>
);
