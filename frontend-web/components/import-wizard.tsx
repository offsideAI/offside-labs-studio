"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import {
  type ImportEntityType,
  type ImportRun,
  useCommitImport,
  useImportRun,
  useUpdateImportMapping,
  useUploadImportCSV,
} from "../lib/api";
import { useActiveWorkspace } from "../lib/contexts";

const CONTACT_FIELDS: Array<{ value: string; label: string }> = [
  { value: "", label: "— skip —" },
  { value: "first_name", label: "First name" },
  { value: "last_name", label: "Last name" },
  { value: "primary_email", label: "Primary email" },
  { value: "title", label: "Title" },
  { value: "lifecycle_stage", label: "Lifecycle stage" },
  { value: "source", label: "Source" },
];

const COMPANY_FIELDS: Array<{ value: string; label: string }> = [
  { value: "", label: "— skip —" },
  { value: "name", label: "Name" },
  { value: "domain", label: "Domain" },
  { value: "industry", label: "Industry" },
  { value: "size_band", label: "Size band" },
];

interface Props {
  entityType: ImportEntityType;
}

export const ImportWizard = ({ entityType }: Props) => {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return (
    <ImportWizardInner
      entityType={entityType}
      workspaceId={active.id}
      workspaceSlug={active.slug}
    />
  );
};

const ImportWizardInner = ({
  entityType,
  workspaceId,
  workspaceSlug,
}: Props & { workspaceId: number; workspaceSlug: string }) => {
  const router = useRouter();
  const [importId, setImportId] = React.useState<number | null>(null);
  const [committed, setCommitted] = React.useState(false);

  const upload = useUploadImportCSV(workspaceId);
  const updateMapping = useUpdateImportMapping(workspaceId);
  const commit = useCommitImport(workspaceId);
  const run = useImportRun(workspaceId, importId, committed);

  const onUpload = async (file: File) => {
    const created = await upload.mutateAsync({ file, entityType });
    setImportId(created.id);
  };

  const fields = entityType === "contact" ? CONTACT_FIELDS : COMPANY_FIELDS;
  const labelForEntity = entityType === "contact" ? "contacts" : "companies";

  return (
    <div className="container-editorial section-rhythm space-y-10 py-12">
      <div>
        <Link href={`/${workspaceSlug}/${labelForEntity}`} className="link-tan text-sm">
          ← {labelForEntity.charAt(0).toUpperCase() + labelForEntity.slice(1)}
        </Link>
      </div>

      <header>
        <Eyebrow>{labelForEntity} · CSV import</Eyebrow>
        <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
          Import from CSV<span className="tan-period">.</span>
        </h1>
        <p className="mt-3 text-fg-muted">
          Upload a UTF-8 CSV with a header row. We&rsquo;ll suggest a column-to-field mapping; you
          confirm and commit. The import runs as a Celery task — refresh-safe, retryable, with
          per-row error reporting.
        </p>
      </header>

      <Hairline />

      {!importId ? (
        <UploadStep onUpload={onUpload} disabled={upload.isPending} />
      ) : run.isLoading || !run.data ? (
        <p className="text-fg-muted">Loading import…</p>
      ) : run.data.status === "pending" ? (
        <MappingStep
          run={run.data}
          fields={fields}
          onSave={(mapping) => updateMapping.mutateAsync({ id: run.data!.id, mapping })}
          onCommit={async () => {
            await commit.mutateAsync(run.data!.id);
            setCommitted(true);
          }}
          saving={updateMapping.isPending}
          committing={commit.isPending}
        />
      ) : (
        <ProgressStep run={run.data} workspaceSlug={workspaceSlug} entity={labelForEntity} />
      )}
    </div>
  );
};

const UploadStep = ({
  onUpload,
  disabled,
}: {
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
}) => {
  const [error, setError] = React.useState<string | null>(null);
  const [uploading, setUploading] = React.useState(false);

  const onChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      await onUpload(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Step 1 of 3</Eyebrow>
        <h2 className="text-2xl font-styrene font-bold">Upload your file.</h2>
      </CardHeader>
      <CardContent>
        <label className="block">
          <span className="text-sm font-medium">CSV file</span>
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={onChange}
            disabled={disabled || uploading}
            className="mt-2 block w-full text-sm file:mr-4 file:rounded-sm file:border file:border-ink file:bg-ink file:px-4 file:py-2 file:font-bold file:text-bone hover:file:bg-ink-700"
          />
          <p className="mt-2 text-xs text-fg-muted">
            UTF-8, header row, comma-delimited. Up to 50,000 rows is supported in M4.
          </p>
        </label>
        {error ? (
          <p role="alert" className="mt-3 text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
};

const MappingStep = ({
  run,
  fields,
  onSave,
  onCommit,
  saving,
  committing,
}: {
  run: ImportRun;
  fields: Array<{ value: string; label: string }>;
  onSave: (mapping: Record<string, string>) => Promise<unknown>;
  onCommit: () => Promise<void>;
  saving: boolean;
  committing: boolean;
}) => {
  const [mapping, setMapping] = React.useState<Record<string, string>>(run.mapping);
  const [error, setError] = React.useState<string | null>(null);

  const setColumn = (idx: number, field: string) => {
    const next = { ...mapping };
    if (field) next[String(idx)] = field;
    else delete next[String(idx)];
    setMapping(next);
  };

  const onCommitClick = async () => {
    setError(null);
    try {
      await onSave(mapping);
      await onCommit();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Commit failed.");
    }
  };

  const mappedCount = Object.keys(mapping).length;

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Step 2 of 3</Eyebrow>
        <h2 className="text-2xl font-styrene font-bold">
          Review the mapping.
        </h2>
        <p className="mt-2 text-sm text-fg-muted">
          {mappedCount} of {run.headers.length} columns mapped · {run.total_rows} rows ready to
          import.
        </p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto rounded-md border hairline">
          <table className="w-full text-sm">
            <thead className="bg-bone/60">
              <tr className="text-left">
                <th className="px-4 py-2 font-styrene text-[11px] uppercase tracking-eyebrow text-tan-text">
                  Column
                </th>
                <th className="px-4 py-2 font-styrene text-[11px] uppercase tracking-eyebrow text-tan-text">
                  → Field
                </th>
                <th className="px-4 py-2 font-styrene text-[11px] uppercase tracking-eyebrow text-tan-text">
                  Sample
                </th>
              </tr>
            </thead>
            <tbody className="divide-y hairline">
              {run.headers.map((header, idx) => (
                <tr key={idx}>
                  <td className="px-4 py-2 font-medium">{header}</td>
                  <td className="px-4 py-2">
                    <select
                      value={mapping[String(idx)] ?? ""}
                      onChange={(e) => setColumn(idx, e.target.value)}
                      className="rounded-sm border hairline bg-bone px-2 py-1 text-sm"
                      aria-label={`Map ${header}`}
                    >
                      {fields.map((f) => (
                        <option key={f.value} value={f.value}>
                          {f.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-fg-muted">
                    {run.sample_rows[0]?.[idx] ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {error ? (
          <p role="alert" className="mt-3 text-sm text-[#8E3B30]">
            {error}
          </p>
        ) : null}

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onCommitClick}
            disabled={committing || saving || mappedCount === 0}
            className="rounded-sm border border-ink bg-ink px-4 py-2 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-50"
          >
            {committing ? "Starting import…" : `Import ${run.total_rows} rows`}
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

const ProgressStep = ({
  run,
  workspaceSlug,
  entity,
}: {
  run: ImportRun;
  workspaceSlug: string;
  entity: string;
}) => {
  const tone =
    run.status === "complete"
      ? "success"
      : run.status === "failed"
        ? "danger"
        : run.status === "running"
          ? "info"
          : "neutral";

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Step 3 of 3</Eyebrow>
        <h2 className="text-2xl font-styrene font-bold">Import progress.</h2>
        <p className="mt-2">
          <StatusPill tone={tone}>{run.status}</StatusPill>
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="h-2 overflow-hidden rounded-full bg-ink/10">
            <div
              className="h-full bg-tan transition-all duration-300"
              style={{ width: `${run.progress_pct}%` }}
            />
          </div>
          <p className="font-mono text-xs text-fg-muted">
            {run.processed_rows} processed · {run.error_rows} errors · {run.total_rows} total
          </p>
        </div>

        {run.errors.length > 0 ? (
          <div className="mt-6">
            <h3 className="font-styrene text-sm font-bold">First error rows</h3>
            <ul className="mt-2 max-h-48 overflow-y-auto rounded-md border hairline bg-bone/60 p-3 font-mono text-xs">
              {run.errors.slice(0, 20).map((e, idx) => (
                <li key={idx} className="py-0.5">
                  row {e.row ?? "—"}: {e.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {run.status === "complete" || run.status === "failed" ? (
          <div className="mt-6">
            <Link
              href={`/${workspaceSlug}/${entity}`}
              className="rounded-sm border border-ink bg-ink px-4 py-2 text-sm font-bold text-bone hover:bg-ink-700"
            >
              Back to {entity}
            </Link>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
};
