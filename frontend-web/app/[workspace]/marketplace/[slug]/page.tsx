"use client";

import { Eyebrow, Hairline } from "@offside/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import {
  type MarketplaceAgentDetail,
  useInstallMarketplaceAgent,
  useMarketplaceAgent,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { WorkflowCanvas } from "../../../../components/workflow-canvas";

const CATEGORY_LABEL: Record<string, string> = {
  lead_management: "Lead management",
  deal_hygiene: "Deal hygiene",
  comms: "Communications",
  integrations: "Integrations",
  operations: "Operations",
};

export default function MarketplaceAgentDetailPage() {
  const params = useParams<{ workspace: string; slug: string }>();
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return (
    <AgentDetail
      slug={params.slug}
      workspaceId={active.id}
      workspaceSlug={active.slug}
    />
  );
}

const AgentDetail = ({
  slug,
  workspaceId,
  workspaceSlug,
}: {
  slug: string;
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const router = useRouter();
  const agentQuery = useMarketplaceAgent(slug);
  const install = useInstallMarketplaceAgent(workspaceId);
  const [error, setError] = React.useState<string | null>(null);

  const agent = agentQuery.data;

  const onInstall = async () => {
    if (!agent) return;
    setError(null);
    try {
      const result = await install.mutateAsync(agent.slug);
      router.push(`/${workspaceSlug}/automations/${result.automation_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Install failed");
    }
  };

  if (agentQuery.isLoading) {
    return <div className="px-6 py-10 text-fg-muted">Loading agent…</div>;
  }
  if (!agent) {
    return (
      <div className="px-6 py-10">
        <p className="text-fg-muted">Agent not found.</p>
        <Link
          href={`/${workspaceSlug}/marketplace`}
          className="mt-2 inline-block text-tan-text underline"
        >
          ← Back to the marketplace
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      <header className="space-y-3 border-b hairline bg-bone px-6 py-6">
        <div className="flex items-center gap-3">
          <Link
            href={`/${workspaceSlug}/marketplace`}
            className="font-mono text-[10px] uppercase tracking-eyebrow text-tan-text hover:underline"
          >
            ← Agent Marketplace
          </Link>
          <span className="font-mono text-[10px] uppercase tracking-eyebrow text-fg-muted">
            {CATEGORY_LABEL[agent.category] ?? agent.category}
          </span>
        </div>

        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="flex items-end gap-4">
            <span className="text-5xl leading-none" aria-hidden>
              {agent.icon_emoji}
            </span>
            <div>
              <h1 className="text-3xl font-styrene font-bold tracking-tight">
                {agent.name}<span className="tan-period">.</span>
              </h1>
              <p className="mt-1 font-mono text-[10px] text-fg-muted">
                by {agent.author} · {agent.install_count} installs
              </p>
            </div>
          </div>

          <div className="flex flex-col items-end gap-2">
            <button
              type="button"
              onClick={onInstall}
              disabled={install.isPending}
              className="inline-flex h-11 items-center rounded-sm border border-ink bg-ink px-5 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
            >
              {install.isPending ? "Installing…" : "Install to workspace"}
            </button>
            {error ? (
              <p className="font-mono text-[10px] text-[#8E3B30]">{error}</p>
            ) : null}
          </div>
        </div>

        <p className="max-w-3xl text-sm text-ink/80">{agent.description}</p>
        {agent.long_description ? (
          <p className="max-w-3xl text-sm text-fg-muted">{agent.long_description}</p>
        ) : null}
      </header>

      <PreviewLabel agent={agent} />

      <div className="relative flex-1 min-h-[420px]">
        <WorkflowCanvas
          graph={agent.graph}
          onChange={() => {
            /* preview is read-only — drag/edit disabled at the canvas level */
          }}
          readOnly
        />
      </div>

      <footer className="border-t hairline bg-bone px-6 py-3">
        <p className="font-mono text-[10px] text-fg-muted">
          Preview shows the agent's v1 graph. Install to get an editable copy
          in your workspace — your changes don't propagate back to the
          marketplace.
        </p>
      </footer>

      <Hairline />
    </div>
  );
};

const PreviewLabel = ({ agent }: { agent: MarketplaceAgentDetail }) => {
  const nodeCount = Object.keys(agent.graph.nodes ?? {}).length;
  const triggerType = (agent.trigger as { type?: string })?.type ?? "manual";
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b hairline bg-bone px-6 py-3 font-mono text-[10px] text-fg-muted">
      <span>
        <span className="uppercase tracking-eyebrow text-tan-text">Trigger</span> ·{" "}
        <span className="text-ink">{triggerType}</span>
      </span>
      <span>
        <span className="uppercase tracking-eyebrow text-tan-text">Nodes</span> ·{" "}
        <span className="text-ink">{nodeCount}</span>
      </span>
      <span>
        <span className="uppercase tracking-eyebrow text-tan-text">Updated</span> ·{" "}
        <span className="text-ink">{new Date(agent.updated_at).toLocaleDateString()}</span>
      </span>
    </div>
  );
};
