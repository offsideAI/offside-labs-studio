"use client";

import { Eyebrow, Hairline, StatusPill, type StatusPillTone } from "@offside/ui";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import {
  type Automation,
  type AutomationStatus,
  useAutomations,
  useCreateAutomation,
} from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

const STATUS_TONE: Record<AutomationStatus, StatusPillTone> = {
  draft: "neutral",
  active: "success",
  paused: "warning",
  archived: "neutral",
};

export default function AutomationsListPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <AutomationsList workspaceId={active.id} workspaceSlug={active.slug} />;
}

const AutomationsList = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const router = useRouter();
  const automations = useAutomations(workspaceId);
  const createAutomation = useCreateAutomation(workspaceId);

  const list = automations.data?.results ?? [];

  const onNew = async () => {
    const draft = await createAutomation.mutateAsync({
      name: "Untitled workflow",
      description: "",
      trigger: { type: "manual" },
      graph: { nodes: {} },
    });
    router.push(`/${workspaceSlug}/automations/${draft.id}`);
  };

  return (
    <div className="space-y-6 px-6 py-8">
      <header className="flex items-end justify-between gap-4">
        <div>
          <Eyebrow>Workflows</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            Automations<span className="tan-period">.</span>
          </h1>
          <p className="mt-2 max-w-prose text-sm text-fg-muted">
            Visual node-graph workflows powered by the durable Celery runtime.
            Draft, publish a version, and watch runs execute.
          </p>
        </div>
        <button
          type="button"
          onClick={onNew}
          disabled={createAutomation.isPending}
          className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
        >
          {createAutomation.isPending ? "Creating…" : "+ New workflow"}
        </button>
      </header>

      <Hairline />

      {automations.isLoading ? (
        <p className="text-fg-muted">Loading…</p>
      ) : list.length === 0 ? (
        <EmptyState onNew={onNew} disabled={createAutomation.isPending} />
      ) : (
        <ul className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {list.map((a) => (
            <AutomationCard key={a.id} automation={a} workspaceSlug={workspaceSlug} />
          ))}
        </ul>
      )}
    </div>
  );
};

const EmptyState = ({ onNew, disabled }: { onNew: () => void; disabled: boolean }) => (
  <div className="rounded-sm border hairline bg-bone p-8 text-center">
    <Eyebrow>Get started</Eyebrow>
    <p className="mt-2 text-sm text-fg-muted">
      You don't have any workflows yet. Build one visually — drag nodes onto
      the canvas, connect them, publish a version, and runs go through the
      durable Celery runtime.
    </p>
    <button
      type="button"
      onClick={onNew}
      disabled={disabled}
      className="mt-4 inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-50"
    >
      Create the first workflow
    </button>
  </div>
);

const AutomationCard = ({
  automation,
  workspaceSlug,
}: {
  automation: Automation;
  workspaceSlug: string;
}) => {
  const nodeCount = Object.keys(automation.graph?.nodes ?? {}).length;
  const tone = STATUS_TONE[automation.status] ?? "neutral";
  return (
    <li>
      <Link
        href={`/${workspaceSlug}/automations/${automation.id}`}
        className="block rounded-sm border hairline bg-bone p-4 shadow-soft-1 transition-colors hover:border-tan focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
      >
        <div className="flex items-center justify-between gap-2">
          <p className="font-styrene text-base font-bold">{automation.name}</p>
          <StatusPill tone={tone}>{automation.status}</StatusPill>
        </div>
        {automation.description ? (
          <p className="mt-1 text-sm text-fg-muted line-clamp-2">{automation.description}</p>
        ) : null}
        <dl className="mt-3 grid grid-cols-3 gap-2 font-mono text-[10px] text-fg-muted">
          <div>
            <dt className="uppercase tracking-eyebrow">Version</dt>
            <dd className="mt-0.5 text-ink">v{automation.version}</dd>
          </div>
          <div>
            <dt className="uppercase tracking-eyebrow">Nodes</dt>
            <dd className="mt-0.5 text-ink">{nodeCount}</dd>
          </div>
          <div>
            <dt className="uppercase tracking-eyebrow">Updated</dt>
            <dd className="mt-0.5 text-ink">
              {new Date(automation.updated_at).toLocaleDateString()}
            </dd>
          </div>
        </dl>
      </Link>
    </li>
  );
};
