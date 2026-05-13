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
  cart_recovery: "Cart recovery",
  comms: "Communications",
  fulfillment: "Fulfillment",
  payments: "Payments",
  customer_service: "Customer service",
  deal_hygiene: "Deal hygiene",
  integrations: "Integrations",
  operations: "Operations",
};

const formatInstallCount = (n: number) => {
  if (n < 1000) return n.toString();
  if (n < 1_000_000) {
    const k = n / 1000;
    return `${k.toFixed(k < 10 ? 1 : 0).replace(/\.0$/, "")}K`;
  }
  return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
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
  const [installed, setInstalled] = React.useState(false);

  const agent = agentQuery.data;

  const onInstall = async () => {
    if (!agent) return;
    setError(null);
    try {
      const result = await install.mutateAsync(agent.slug);
      setInstalled(true);
      // Brief success state before navigating, so the audience sees the
      // confirmation. 600ms is short enough to feel responsive.
      window.setTimeout(() => {
        router.push(`/${workspaceSlug}/automations/${result.automation_id}`);
      }, 600);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Install failed");
    }
  };

  if (agentQuery.isLoading) {
    return <DetailSkeleton />;
  }
  if (!agent) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16 md:px-10">
        <Eyebrow>Not found</Eyebrow>
        <h1 className="mt-3 font-styrene text-3xl font-bold">
          Agent not found<span className="tan-period">.</span>
        </h1>
        <p className="mt-3 text-fg-muted">
          The agent you're looking for isn't in the marketplace. It may have
          been retired or never existed.
        </p>
        <Link
          href={`/${workspaceSlug}/marketplace`}
          className="mt-6 inline-flex h-10 items-center rounded-sm border hairline bg-bone px-4 text-sm font-medium hover:border-tan focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
        >
          ← Back to the marketplace
        </Link>
      </div>
    );
  }

  const nodeCount = Object.keys(agent.graph.nodes ?? {}).length;
  const triggerType = (agent.trigger as { type?: string })?.type ?? "manual";

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 md:px-10">
      {/* Breadcrumb / back link. */}
      <div className="flex items-center justify-between gap-3 pt-8">
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

      {/* HERO — generous icon + name + author + install CTA. */}
      <header className="mt-8 grid gap-10 md:grid-cols-[1fr_auto] md:items-start">
        <div className="flex items-start gap-6 md:gap-8">
          <div
            className="flex h-24 w-24 shrink-0 items-center justify-center rounded-md border hairline bg-bone text-6xl shadow-soft-2 md:h-28 md:w-28 md:text-7xl"
            aria-hidden
          >
            {agent.icon_emoji}
          </div>
          <div className="min-w-0 space-y-3 pt-1">
            <Eyebrow>{CATEGORY_LABEL[agent.category] ?? agent.category}</Eyebrow>
            <h1 className="font-styrene text-4xl font-bold leading-tight tracking-tight md:text-5xl">
              {agent.name}<span className="tan-period">.</span>
            </h1>
            <p className="max-w-2xl text-base leading-relaxed text-fg-muted md:text-lg">
              {agent.description}
            </p>
            <div className="flex flex-wrap items-baseline gap-x-5 gap-y-1 pt-2 font-mono text-[11px] text-fg-muted">
              <span>
                <span className="uppercase tracking-eyebrow text-tan-text">By</span>{" "}
                <span className="text-ink">{agent.author}</span>
              </span>
              <span className="text-fg-muted/50">·</span>
              <span>
                <span className="tabular-nums text-ink">
                  {formatInstallCount(agent.install_count)}
                </span>{" "}
                <span className="uppercase tracking-eyebrow text-tan-text">
                  installs
                </span>
              </span>
            </div>
          </div>
        </div>

        {/* Install CTA — anchored top-right on desktop. */}
        <aside className="md:sticky md:top-20 md:w-[280px]">
          <InstallPanel
            onInstall={onInstall}
            isPending={install.isPending}
            installed={installed}
            error={error}
            nodeCount={nodeCount}
            triggerType={triggerType}
            updatedAt={agent.updated_at}
          />
        </aside>
      </header>

      {/* Long description, if any. */}
      {agent.long_description ? (
        <section className="mt-12 max-w-3xl">
          <Eyebrow>About this agent</Eyebrow>
          <p className="mt-3 whitespace-pre-line text-base leading-relaxed text-ink/85">
            {agent.long_description}
          </p>
        </section>
      ) : null}

      <Hairline className="my-14" />

      {/* Canvas preview — framed. */}
      <section>
        <div className="flex items-end justify-between gap-3">
          <Eyebrow>Graph preview</Eyebrow>
          <p className="font-mono text-[10px] text-fg-muted">
            Read-only. Installs create an editable copy.
          </p>
        </div>
        <div className="mt-3 overflow-hidden rounded-md border hairline bg-bone shadow-soft-2">
          <div className="relative h-[520px]">
            <WorkflowCanvas
              graph={agent.graph}
              onChange={() => {
                /* read-only — canvas refuses edits */
              }}
              readOnly
            />
          </div>
        </div>
        <p className="mt-4 max-w-3xl text-sm text-fg-muted">
          The preview shows the agent's v1 graph as it will land in your
          workspace. Every node — including the {nodeCount}-step
          choreography — is editable in the Agent Design Studio after install.
          Your changes don't propagate back to the marketplace.
        </p>
      </section>
    </div>
  );
};

const InstallPanel = ({
  onInstall,
  isPending,
  installed,
  error,
  nodeCount,
  triggerType,
  updatedAt,
}: {
  onInstall: () => void;
  isPending: boolean;
  installed: boolean;
  error: string | null;
  nodeCount: number;
  triggerType: string;
  updatedAt: string;
}) => (
  <div className="rounded-md border hairline bg-bone p-5 shadow-soft-2">
    <button
      type="button"
      onClick={onInstall}
      disabled={isPending || installed}
      className={
        "inline-flex h-12 w-full items-center justify-center gap-2 rounded-sm border border-ink px-5 text-sm font-bold transition-all duration-200 ease-out-quint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 active:scale-[0.98] disabled:cursor-not-allowed " +
        (installed
          ? "bg-bone text-ink"
          : isPending
            ? "bg-ink text-bone opacity-80"
            : "bg-ink text-bone hover:bg-ink-700 hover:shadow-soft-2")
      }
    >
      {installed ? (
        <>
          <CheckIcon />
          Installed
        </>
      ) : isPending ? (
        <>
          <Spinner />
          Installing…
        </>
      ) : (
        <>
          Install to workspace
          <ArrowRight />
        </>
      )}
    </button>
    {error ? (
      <p className="mt-3 font-mono text-[10px] text-[#8E3B30]">{error}</p>
    ) : null}

    <dl className="mt-5 space-y-3 border-t hairline pt-4 font-mono text-[10px] text-fg-muted">
      <Stat label="Trigger" value={triggerType} />
      <Stat label="Nodes" value={String(nodeCount)} />
      <Stat label="Updated" value={new Date(updatedAt).toLocaleDateString()} />
    </dl>
  </div>
);

const Stat = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-baseline justify-between gap-3">
    <dt className="uppercase tracking-eyebrow text-tan-text">{label}</dt>
    <dd className="tabular-nums text-ink">{value}</dd>
  </div>
);

const Spinner = () => (
  <svg
    aria-hidden
    className="h-4 w-4 animate-spin"
    viewBox="0 0 24 24"
    fill="none"
  >
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeOpacity="0.25"
      strokeWidth="3"
    />
    <path
      d="M22 12a10 10 0 0 1-10 10"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
    />
  </svg>
);

const CheckIcon = () => (
  <svg
    aria-hidden
    className="h-4 w-4"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M5 12.5l5 5 9-11" />
  </svg>
);

const ArrowRight = () => (
  <svg
    aria-hidden
    className="h-4 w-4 transition-transform duration-200 ease-out-quint group-hover:translate-x-0.5"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M5 12h14" />
    <path d="M13 5l7 7-7 7" />
  </svg>
);

const DetailSkeleton = () => (
  <div className="mx-auto max-w-7xl px-6 pb-24 pt-8 md:px-10" aria-busy>
    <div className="h-3 w-32 animate-shimmer rounded-sm" />
    <div className="mt-8 flex items-start gap-6 md:gap-8">
      <div className="h-24 w-24 animate-shimmer rounded-md md:h-28 md:w-28" />
      <div className="min-w-0 flex-1 space-y-3 pt-2">
        <div className="h-3 w-24 animate-shimmer rounded-sm" />
        <div className="h-10 w-3/4 animate-shimmer rounded-sm" />
        <div className="h-3 w-full max-w-2xl animate-shimmer rounded-sm" />
        <div className="h-3 w-3/4 max-w-2xl animate-shimmer rounded-sm" />
      </div>
    </div>
    <div className="mt-14 h-[520px] animate-shimmer rounded-md" />
  </div>
);
