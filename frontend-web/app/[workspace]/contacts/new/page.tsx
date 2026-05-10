"use client";

import { Eyebrow } from "@offside/ui";
import { useRouter } from "next/navigation";
import * as React from "react";

import { useCreateContact, useCompanies } from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { CustomFieldsPanel } from "../../../../components/custom-fields-panel";

const LIFECYCLE_STAGES = [
  { value: "", label: "—" },
  { value: "lead", label: "Lead" },
  { value: "qualified", label: "Qualified" },
  { value: "customer", label: "Customer" },
  { value: "churned", label: "Churned" },
];

export default function NewContactPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <NewContactForm workspaceId={active.id} workspaceSlug={active.slug} />;
}

const NewContactForm = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const router = useRouter();
  const create = useCreateContact(workspaceId);
  const companies = useCompanies(workspaceId);

  const [firstName, setFirstName] = React.useState("");
  const [lastName, setLastName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [title, setTitle] = React.useState("");
  const [companyId, setCompanyId] = React.useState<string>("");
  const [stage, setStage] = React.useState("");
  const [custom, setCustom] = React.useState<Record<string, unknown>>({});
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const created = await create.mutateAsync({
        first_name: firstName,
        last_name: lastName,
        primary_email: email,
        title,
        company: companyId ? Number(companyId) : null,
        lifecycle_stage: stage,
        custom,
      });
      router.replace(`/${workspaceSlug}/contacts/${created.id}`);
    } catch {
      setError("Could not create contact.");
    }
  };

  return (
    <div className="container-editorial section-rhythm max-w-xl py-12">
      <Eyebrow>New contact</Eyebrow>
      <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight">Add a contact<span className="tan-period">.</span></h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Row>
          <Field label="First name" htmlFor="first_name">
            <input
              id="first_name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="input"
            />
          </Field>
          <Field label="Last name" htmlFor="last_name">
            <input
              id="last_name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="input"
            />
          </Field>
        </Row>
        <Field label="Primary email" htmlFor="email">
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </Field>
        <Row>
          <Field label="Title" htmlFor="title">
            <input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input"
            />
          </Field>
          <Field label="Company" htmlFor="company">
            <select
              id="company"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="input"
            >
              <option value="">—</option>
              {(companies.data?.results ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
        </Row>
        <Field label="Lifecycle stage" htmlFor="stage">
          <select
            id="stage"
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            className="input"
          >
            {LIFECYCLE_STAGES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </Field>

        <CustomFieldsPanel
          workspaceId={workspaceId}
          entityType="contact"
          values={custom}
          onChange={setCustom}
        />

        {error ? (
          <p role="alert" className="text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={create.isPending} className="button-primary">
            {create.isPending ? "Creating…" : "Create contact"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-sm border hairline bg-bone px-4 py-2 text-sm font-medium hover:bg-tan-100"
          >
            Cancel
          </button>
        </div>
      </form>

      <style jsx>{`
        .input {
          width: 100%;
          padding: 0.5rem 0.75rem;
          background: var(--brand-bone);
          border: 1px solid var(--brand-rule);
          border-radius: 4px;
          color: var(--brand-ink);
          font-size: 0.9rem;
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
          padding: 0.5rem 1.25rem;
          font-weight: 700;
          cursor: pointer;
        }
        .button-primary:hover { background: #303030; }
        .button-primary:disabled { opacity: 0.6; cursor: not-allowed; }
      `}</style>
    </div>
  );
};

const Row = ({ children }: { children: React.ReactNode }) => (
  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">{children}</div>
);

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
