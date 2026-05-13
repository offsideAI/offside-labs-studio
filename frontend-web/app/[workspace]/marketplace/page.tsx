"use client";

import { Eyebrow, Hairline } from "@offside/ui";
import Link from "next/link";
import * as React from "react";

import {
  type MarketplaceAgentCategory,
  type MarketplaceAgentSummary,
  useMarketplaceAgents,
} from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

const CATEGORY_LABELS: Record<MarketplaceAgentCategory, string> = {
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

// Display order — leads with the e-commerce lifecycle stages
// (lead → conversion → fulfillment → payments → service) so a
// browsing admin can scan the catalog top-to-bottom in the order
// they're most likely to think about their funnel.
const CATEGORIES: MarketplaceAgentCategory[] = [
  "lead_management",
  "cart_recovery",
  "comms",
  "fulfillment",
  "payments",
  "customer_service",
  "deal_hygiene",
  "integrations",
  "operations",
];

export default function MarketplacePage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <MarketplaceGrid workspaceSlug={active.slug} />;
}

const MarketplaceGrid = ({ workspaceSlug }: { workspaceSlug: string }) => {
  const [category, setCategory] = React.useState<MarketplaceAgentCategory | null>(null);
  const agents = useMarketplaceAgents(category ?? undefined);
  const list = agents.data?.results ?? [];

  return (
    <div className="space-y-8 px-6 py-10">
      <header className="space-y-3">
        <Eyebrow>OffsideStudio</Eyebrow>
        <h1 className="text-4xl font-styrene font-bold tracking-tight md:text-5xl">
          Agent Marketplace<span className="tan-period">.</span>
        </h1>
        <p className="max-w-2xl text-base text-fg-muted">
          Install a pre-built agent, customize it in the Agent Design Studio,
          watch it run against your CRM. One click from this catalog to a
          published, runnable workflow in your workspace.
        </p>
      </header>

      <Hairline />

      <CategoryFilter active={category} onChange={setCategory} />

      {agents.isLoading ? (
        <SkeletonGrid />
      ) : list.length === 0 ? (
        <p className="rounded-sm border hairline bg-bone px-6 py-12 text-center text-fg-muted">
          No agents in this category yet.
        </p>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {list.map((agent) => (
            <AgentCard key={agent.id} agent={agent} workspaceSlug={workspaceSlug} />
          ))}
        </ul>
      )}
    </div>
  );
};

const CategoryFilter = ({
  active,
  onChange,
}: {
  active: MarketplaceAgentCategory | null;
  onChange: (next: MarketplaceAgentCategory | null) => void;
}) => (
  <div className="flex flex-wrap items-center gap-2">
    <FilterChip selected={active === null} onClick={() => onChange(null)}>
      All
    </FilterChip>
    {CATEGORIES.map((c) => (
      <FilterChip key={c} selected={active === c} onClick={() => onChange(c)}>
        {CATEGORY_LABELS[c]}
      </FilterChip>
    ))}
  </div>
);

const FilterChip = ({
  selected,
  onClick,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) => (
  <button
    type="button"
    onClick={onClick}
    className={
      "rounded-sm border px-3 py-1.5 text-xs font-medium transition-colors " +
      (selected
        ? "border-ink bg-ink text-bone"
        : "hairline bg-bone text-fg-muted hover:border-tan hover:text-ink")
    }
  >
    {children}
  </button>
);

const AgentCard = ({
  agent,
  workspaceSlug,
}: {
  agent: MarketplaceAgentSummary;
  workspaceSlug: string;
}) => (
  <li>
    <Link
      href={`/${workspaceSlug}/marketplace/${agent.slug}`}
      className="block h-full rounded-sm border hairline bg-bone p-5 shadow-soft-1 transition-all hover:border-tan hover:shadow-soft-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-3xl leading-none" aria-hidden>
          {agent.icon_emoji}
        </span>
        <span className="font-mono text-[10px] uppercase tracking-eyebrow text-tan-text">
          {agent.install_count} installs
        </span>
      </div>
      <p className="mt-3 font-styrene text-lg font-bold">{agent.name}</p>
      <p className="mt-1 text-sm text-fg-muted line-clamp-3">{agent.description}</p>
      <div className="mt-4 flex items-center justify-between gap-3 font-mono text-[10px]">
        <span className="uppercase tracking-eyebrow text-tan-text">
          {CATEGORY_LABELS[agent.category]}
        </span>
        <span className="text-fg-muted">{agent.author}</span>
      </div>
    </Link>
  </li>
);

const SkeletonGrid = () => (
  <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <li key={i} className="h-44 animate-pulse rounded-sm border hairline bg-bone/60" />
    ))}
  </ul>
);
