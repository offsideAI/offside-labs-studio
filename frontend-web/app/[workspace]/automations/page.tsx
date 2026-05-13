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
          <Eyebrow>OffsideStudio</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            Agent Design Studio<span className="tan-period">.</span>
          </h1>
          <p className="mt-2 max-w-prose text-sm text-fg-muted">
            Design, customize, and observe every agent in your workspace.
            Start from the Agent Marketplace, describe an agent in English,
            or build one from scratch on the canvas.
          </p>
        </div>
        <div className="flex items-end gap-2">
          <Link
            href={`/${workspaceSlug}/marketplace`}
            className="inline-flex h-10 items-center rounded-sm border hairline bg-bone px-4 text-sm font-medium hover:border-tan focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan"
          >
            Browse Marketplace
          </Link>
          <button
            type="button"
            onClick={onNew}
            disabled={createAutomation.isPending}
            className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
          >
            {createAutomation.isPending ? "Creating…" : "+ Blank workflow"}
          </button>
        </div>
      </header>

      <Hairline />

      {automations.isLoading ? (
        <p className="text-fg-muted">Loading…</p>
      ) : list.length === 0 ? (
        <EmptyState
          onNew={onNew}
          disabled={createAutomation.isPending}
          workspaceSlug={workspaceSlug}
        />
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

const EmptyState = ({
  onNew,
  disabled,
  workspaceSlug,
}: {
  onNew: () => void;
  disabled: boolean;
  workspaceSlug: string;
}) => (
  <div className="rounded-sm border hairline bg-bone p-10 text-center">
    <Eyebrow>OffsideStudio · Get started</Eyebrow>
    <h2 className="mt-3 font-styrene text-2xl font-bold">
      Install your first agent from the Marketplace<span className="tan-period">.</span>
    </h2>
    <p className="mt-3 mx-auto max-w-xl text-sm text-fg-muted">
      The fastest path to a running workflow: pick a pre-built agent from
      the Agent Marketplace and install it in one click. It lands here as
      an editable, published workflow. You can also describe an agent in
      English to Claude, or build one from scratch on the canvas.
    </p>
    <div className="mt-6 flex items-center justify-center gap-2">
      <Link
        href={`/${workspaceSlug}/marketplace`}
        className="inline-flex h-11 items-center rounded-sm border border-ink bg-ink px-5 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
      >
        Open the Marketplace
      </Link>
      <button
        type="button"
        onClick={onNew}
        disabled={disabled}
        className="inline-flex h-11 items-center rounded-sm border hairline bg-bone px-5 text-sm font-medium hover:border-tan disabled:opacity-50"
      >
        Or start with a blank canvas
      </button>
    </div>
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
