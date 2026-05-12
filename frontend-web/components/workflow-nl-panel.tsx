"use client";

import { Eyebrow } from "@offside/ui";
import * as React from "react";

import type { AutomationGraph, GenerateFromNLResponse } from "../lib/api";

interface Props {
  open: boolean;
  isPending: boolean;
  error: string | null;
  preview: GenerateFromNLResponse | null;
  onGenerate: (description: string) => void;
  onApply: () => void;
  onDiscard: () => void;
  onClose: () => void;
}

const EXAMPLES = [
  "When a new contact is created, log it and wait 5 minutes before moving the related deal to qualified.",
  "After a deal hits 'demo', ask for manager approval before moving it to negotiation.",
  "If a contact's score is greater than 80, branch into the high-value path; otherwise end.",
];

export const WorkflowNLPanel = ({
  open,
  isPending,
  error,
  preview,
  onGenerate,
  onApply,
  onDiscard,
  onClose,
}: Props) => {
  const [description, setDescription] = React.useState("");

  if (!open) return null;

  const previewNodes = preview ? Object.keys(preview.graph.nodes ?? {}).length : 0;

  return (
    <div className="border-b hairline bg-bone">
      <div className="grid gap-4 px-6 py-4 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div>
          <div className="flex items-start justify-between gap-3">
            <div>
              <Eyebrow>Describe in English</Eyebrow>
              <p className="mt-1 font-mono text-[10px] text-fg-muted">
                Claude proposes a graph. Review it before it touches your canvas.
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="font-mono text-[10px] uppercase tracking-eyebrow text-fg-muted hover:text-ink"
            >
              Close
            </button>
          </div>

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            placeholder="e.g. When a deal hits 'demo', ask the owner for approval and notify Slack on approve."
            disabled={isPending}
            className="mt-3 block w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus:border-tan focus:outline-none focus:ring-1 focus:ring-tan disabled:opacity-50"
          />

          <div className="mt-2 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => description.trim() && onGenerate(description.trim())}
              disabled={isPending || !description.trim()}
              className="inline-flex h-9 items-center rounded-sm border border-ink bg-ink px-3 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
            >
              {isPending ? "Generating…" : "Generate"}
            </button>
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                disabled={isPending}
                onClick={() => setDescription(ex)}
                className="rounded-sm border hairline bg-bone px-2 py-1 text-[11px] text-fg-muted hover:border-tan hover:text-ink disabled:opacity-50"
              >
                {ex.slice(0, 56)}…
              </button>
            ))}
          </div>

          {error ? (
            <p className="mt-2 font-mono text-[11px] text-[#8E3B30]">{error}</p>
          ) : null}
        </div>

        <div className="border-l hairline pl-4">
          <Eyebrow>Preview</Eyebrow>
          {!preview ? (
            <p className="mt-2 font-mono text-[11px] text-fg-muted">
              The proposed graph will appear here. Apply replaces your draft;
              Discard leaves it alone.
            </p>
          ) : (
            <>
              <p className="mt-1 font-mono text-[10px] text-fg-muted">
                {previewNodes} {previewNodes === 1 ? "node" : "nodes"} · {preview.tokens_in}↓ / {preview.tokens_out}↑ tokens · {preview.latency_ms} ms · {preview.model}
              </p>
              <pre className="mt-2 max-h-40 overflow-auto rounded-sm border hairline bg-bone px-3 py-2 font-mono text-[10px] leading-relaxed text-ink/80">
                {JSON.stringify(preview.graph, null, 2)}
              </pre>
              <div className="mt-2 flex items-center gap-2">
                <button
                  type="button"
                  onClick={onApply}
                  className="inline-flex h-9 items-center rounded-sm border border-ink bg-ink px-3 text-sm font-bold text-bone hover:bg-ink-700"
                >
                  Apply to canvas
                </button>
                <button
                  type="button"
                  onClick={onDiscard}
                  className="inline-flex h-9 items-center rounded-sm border hairline bg-bone px-3 text-sm font-medium hover:border-tan"
                >
                  Discard
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
