"use client";

import { Eyebrow } from "@offside/ui";
import { useRouter } from "next/navigation";
import * as React from "react";

import {
  useCompanies,
  useContacts,
  useCreateDeal,
  usePipelines,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";

export default function NewDealPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <NewDealForm workspaceId={active.id} workspaceSlug={active.slug} />;
}

const NewDealForm = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const router = useRouter();
  const create = useCreateDeal(workspaceId);
  const pipelines = usePipelines(workspaceId);
  const contacts = useContacts(workspaceId);
  const companies = useCompanies(workspaceId);

  const [name, setName] = React.useState("");
  const [pipelineId, setPipelineId] = React.useState<string>("");
  const [stageId, setStageId] = React.useState<string>("");
  const [valueDollars, setValueDollars] = React.useState("");
  const [contactId, setContactId] = React.useState<string>("");
  const [companyId, setCompanyId] = React.useState<string>("");
  const [error, setError] = React.useState<string | null>(null);

  const pipelineList = pipelines.data?.results ?? [];
  React.useEffect(() => {
    if (pipelineId) return;
    const first = pipelineList.find((p) => p.is_default) ?? pipelineList[0];
    if (first) {
      setPipelineId(String(first.id));
      setStageId(first.stages[0]?.id ?? "");
    }
  }, [pipelineList, pipelineId]);

  const activePipeline = pipelineList.find((p) => String(p.id) === pipelineId);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!pipelineId || !stageId) {
      setError("Pick a pipeline + stage.");
      return;
    }
    try {
      const valueCents = valueDollars ? Math.round(Number(valueDollars) * 100) : 0;
      const created = await create.mutateAsync({
        name,
        pipeline: Number(pipelineId),
        stage_id: stageId,
        value_cents: valueCents,
        currency: "USD",
        contact: contactId ? Number(contactId) : null,
        company: companyId ? Number(companyId) : null,
      });
      router.replace(`/${workspaceSlug}/deals/${created.id}`);
    } catch {
      setError("Could not create deal.");
    }
  };

  return (
    <div className="container-editorial max-w-xl py-12">
      <Eyebrow>New deal</Eyebrow>
      <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight">
        Add a deal<span className="tan-period">.</span>
      </h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Field label="Name" htmlFor="name">
          <input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="input"
          />
        </Field>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Pipeline" htmlFor="pipeline">
            <select
              id="pipeline"
              value={pipelineId}
              onChange={(e) => {
                setPipelineId(e.target.value);
                const next = pipelineList.find((p) => String(p.id) === e.target.value);
                setStageId(next?.stages[0]?.id ?? "");
              }}
              className="input"
              required
            >
              <option value="">—</option>
              {pipelineList.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Stage" htmlFor="stage">
            <select
              id="stage"
              value={stageId}
              onChange={(e) => setStageId(e.target.value)}
              className="input"
              required
            >
              <option value="">—</option>
              {(activePipeline?.stages ?? [])
                .slice()
                .sort((a, b) => a.order - b.order)
                .map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
            </select>
          </Field>
        </div>
        <Field label="Value (USD)" htmlFor="value">
          <input
            id="value"
            type="number"
            step="0.01"
            min="0"
            value={valueDollars}
            onChange={(e) => setValueDollars(e.target.value)}
            placeholder="24000"
            className="input"
          />
        </Field>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Contact" htmlFor="contact">
            <select
              id="contact"
              value={contactId}
              onChange={(e) => setContactId(e.target.value)}
              className="input"
            >
              <option value="">—</option>
              {(contacts.data?.results ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {`${c.first_name} ${c.last_name}`.trim() || c.primary_email}
                </option>
              ))}
            </select>
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
        </div>

        {error ? (
          <p role="alert" className="text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={create.isPending} className="button-primary">
            {create.isPending ? "Creating…" : "Create deal"}
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
