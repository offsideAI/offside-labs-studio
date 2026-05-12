"use client";

import { Eyebrow } from "@offside/ui";
import * as React from "react";

import type { AutomationVersion } from "../lib/api";

interface Props {
  open: boolean;
  versions: AutomationVersion[];
  publishedVersionId: number | null;
  isLoading: boolean;
  onClose: () => void;
}

export const WorkflowVersionsPanel = ({
  open,
  versions,
  publishedVersionId,
  isLoading,
  onClose,
}: Props) => {
  const [selected, setSelected] = React.useState<AutomationVersion | null>(null);

  React.useEffect(() => {
    if (!open) setSelected(null);
  }, [open]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-label="Published versions"
      className="absolute inset-y-0 right-0 z-20 flex w-[420px] flex-col border-l hairline bg-bone shadow-soft-3"
    >
      <header className="flex items-start justify-between gap-3 border-b hairline px-4 py-3">
        <div>
          <Eyebrow>Versions</Eyebrow>
          <p className="mt-1 font-mono text-[10px] text-fg-muted">
            Immutable snapshots created by Publish.
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="font-mono text-[10px] uppercase tracking-eyebrow text-fg-muted hover:text-ink"
          aria-label="Close versions panel"
        >
          Close
        </button>
      </header>

      <div className="grid min-h-0 flex-1 grid-rows-[auto_minmax(0,1fr)]">
        <ol className="max-h-[40%] overflow-y-auto border-b hairline">
          {isLoading ? (
            <li className="px-4 py-3 text-sm text-fg-muted">Loading versions…</li>
          ) : versions.length === 0 ? (
            <li className="px-4 py-3 text-sm text-fg-muted">
              No versions yet. Publish the draft to create v1.
            </li>
          ) : (
            versions.map((v) => {
              const isPublished = v.id === publishedVersionId;
              const isSelected = selected?.id === v.id;
              return (
                <li key={v.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(v)}
                    className={
                      "flex w-full items-center justify-between gap-3 border-b hairline px-4 py-2 text-left transition-colors hover:bg-tan-100/40 " +
                      (isSelected ? "bg-tan-100/60" : "")
                    }
                  >
                    <div className="min-w-0">
                      <p className="font-styrene text-sm font-bold">v{v.version_number}</p>
                      <p className="font-mono text-[10px] text-fg-muted">
                        {new Date(v.published_at).toLocaleString()} ·{" "}
                        published by user #{v.published_by}
                      </p>
                    </div>
                    {isPublished ? (
                      <span className="rounded-sm border border-tan px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-eyebrow text-tan-text">
                        current
                      </span>
                    ) : null}
                  </button>
                </li>
              );
            })
          )}
        </ol>

        <div className="overflow-y-auto p-4">
          {selected ? (
            <VersionDetail version={selected} />
          ) : (
            <p className="font-mono text-[11px] text-fg-muted">
              Select a version to inspect its frozen graph and trigger config.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

const VersionDetail = ({ version }: { version: AutomationVersion }) => {
  const nodeCount = Object.keys(version.graph.nodes ?? {}).length;
  return (
    <div className="space-y-3">
      <div>
        <Eyebrow>Frozen graph</Eyebrow>
        <p className="mt-1 font-mono text-[11px] text-fg-muted">
          v{version.version_number} · {nodeCount} {nodeCount === 1 ? "node" : "nodes"} ·{" "}
          start={version.graph.start_node_id ?? "—"}
        </p>
      </div>
      <JsonBlock label="graph" value={version.graph} />
      <JsonBlock label="trigger" value={version.trigger} />
    </div>
  );
};

const JsonBlock = ({ label, value }: { label: string; value: unknown }) => (
  <details className="rounded-sm border hairline bg-bone">
    <summary className="cursor-pointer px-3 py-2 font-mono text-[10px] uppercase tracking-eyebrow text-tan-text">
      {label}
    </summary>
    <pre className="max-h-64 overflow-auto border-t hairline px-3 py-2 font-mono text-[10px] leading-relaxed text-ink/80">
      {JSON.stringify(value, null, 2)}
    </pre>
  </details>
);
