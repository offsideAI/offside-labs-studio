"use client";

import { Eyebrow } from "@offside/ui";
import { useRouter } from "next/navigation";
import * as React from "react";

import { useCreateCompany } from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { CustomFieldsPanel } from "../../../../components/custom-fields-panel";

const SIZE_BANDS = ["", "1-10", "11-50", "51-200", "201-1000", "1000+"];

export default function NewCompanyPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <NewCompanyForm workspaceId={active.id} workspaceSlug={active.slug} />;
}

const NewCompanyForm = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const router = useRouter();
  const create = useCreateCompany(workspaceId);

  const [name, setName] = React.useState("");
  const [domain, setDomain] = React.useState("");
  const [industry, setIndustry] = React.useState("");
  const [sizeBand, setSizeBand] = React.useState("");
  const [custom, setCustom] = React.useState<Record<string, unknown>>({});
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const created = await create.mutateAsync({
        name,
        domain,
        industry,
        size_band: sizeBand,
        custom,
      });
      router.replace(`/${workspaceSlug}/companies/${created.id}`);
    } catch {
      setError("Could not create company.");
    }
  };

  return (
    <div className="container-editorial section-rhythm max-w-xl py-12">
      <Eyebrow>New company</Eyebrow>
      <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight">Add a company<span className="tan-period">.</span></h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="name" className="text-sm font-medium">Name</label>
          <input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="input"
          />
        </div>
        <div className="space-y-1.5">
          <label htmlFor="domain" className="text-sm font-medium">Domain</label>
          <input
            id="domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="acme.com"
            className="input"
          />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <label htmlFor="industry" className="text-sm font-medium">Industry</label>
            <input
              id="industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="input"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="size_band" className="text-sm font-medium">Size band</label>
            <select
              id="size_band"
              value={sizeBand}
              onChange={(e) => setSizeBand(e.target.value)}
              className="input"
            >
              {SIZE_BANDS.map((s) => (
                <option key={s} value={s}>
                  {s || "—"}
                </option>
              ))}
            </select>
          </div>
        </div>

        <CustomFieldsPanel
          workspaceId={workspaceId}
          entityType="company"
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
            {create.isPending ? "Creating…" : "Create company"}
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
