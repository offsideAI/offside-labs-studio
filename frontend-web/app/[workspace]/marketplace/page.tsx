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
// browsing admin scans the catalog top-to-bottom in funnel order.
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

const formatInstallCount = (n: number) => {
  if (n < 1000) return n.toString();
  if (n < 1_000_000) {
    const k = n / 1000;
    return `${k.toFixed(k < 10 ? 1 : 0).replace(/\.0$/, "")}K`;
  }
  return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
};

export default function MarketplacePage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <MarketplaceGrid workspaceSlug={active.slug} />;
}

const MarketplaceGrid = ({ workspaceSlug }: { workspaceSlug: string }) => {
  const [category, setCategory] = React.useState<MarketplaceAgentCategory | null>(null);
  const agents = useMarketplaceAgents(category ?? undefined);
  const list = agents.data?.results ?? [];
  const totalInstalls = React.useMemo(
    () => list.reduce((sum, a) => sum + (a.install_count ?? 0), 0),
    [list],
  );

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 pt-16 md:px-10 md:pt-24">
      {/* HERO — Resend-inspired editorial serif, "announcing" pill, generous whitespace. */}
      <header className="space-y-6">
        {/* Announcing pill — pill-shaped chip with chevron, subtle border. */}
        <a
          href="#"
          onClick={(e) => e.preventDefault()}
          className="group inline-flex items-center gap-2 rounded-full border hairline bg-bone px-4 py-1.5 text-xs text-fg-muted transition-all duration-200 hover:border-tan hover:text-ink dark:bg-[var(--surface-elevated)]"
        >
          <span className="inline-flex h-1.5 w-1.5 rounded-full bg-tan" aria-hidden />
          <span className="font-mono uppercase tracking-eyebrow text-tan-text">Announcing</span>
          <span>Agent Marketplace v1 · 15 curated agents</span>
          <span aria-hidden className="text-fg-muted transition-transform group-hover:translate-x-0.5">→</span>
        </a>

        {/* Editorial serif headline — Resend-style. Tan period preserved. */}
        <h1 className="max-w-4xl font-serif text-5xl font-normal leading-[1.05] tracking-tight md:text-7xl">
          Agents that ship your entire funnel<span className="tan-period">.</span>
        </h1>

        <p className="max-w-2xl text-lg leading-relaxed text-fg-muted md:text-xl">
          Curated agents spanning the full ecommerce lifecycle — lead capture,
          cart recovery, fulfillment, payments, customer service. Install one
          with a click. Customize every step in the Agent Design Studio.
          Every lead becomes a tracked conversion against your CRM.
        </p>

        {/* Stats strip — mono numbers, tabular. */}
        <dl className="flex flex-wrap items-baseline gap-x-8 gap-y-3 pt-3 font-mono text-[11px] text-fg-muted">
          <div>
            <dt className="uppercase tracking-eyebrow text-tan-text">Agents</dt>
            <dd className="mt-1 text-2xl font-styrene font-bold text-ink tabular-nums">
              {agents.isLoading ? "—" : list.length}
            </dd>
          </div>
          <div>
            <dt className="uppercase tracking-eyebrow text-tan-text">Categories</dt>
            <dd className="mt-1 text-2xl font-styrene font-bold text-ink tabular-nums">
              {CATEGORIES.length}
            </dd>
          </div>
          <div>
            <dt className="uppercase tracking-eyebrow text-tan-text">Installs</dt>
            <dd className="mt-1 text-2xl font-styrene font-bold text-ink tabular-nums">
              {agents.isLoading ? "—" : formatInstallCount(totalInstalls)}
            </dd>
          </div>
          <div>
            <dt className="uppercase tracking-eyebrow text-tan-text">Curated by</dt>
            <dd className="mt-1 text-2xl font-styrene font-bold text-ink">
              Offside Labs
            </dd>
          </div>
        </dl>
      </header>

      <Hairline className="my-10 md:my-14" />

      {/* Filter strip — sticky on scroll for desktop. */}
      <div className="sticky top-14 z-10 -mx-6 mb-8 border-b hairline bg-bone/85 px-6 py-3 backdrop-blur md:-mx-10 md:px-10">
        <CategoryFilter active={category} onChange={setCategory} />
      </div>

      {/* Grid. */}
      {agents.isLoading ? (
        <SkeletonGrid />
      ) : list.length === 0 ? (
        <EmptyState />
      ) : (
        <ul className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
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
  <div
    role="tablist"
    aria-label="Filter agents by category"
    className="flex flex-wrap items-center gap-2"
  >
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
    role="tab"
    aria-selected={selected}
    onClick={onClick}
    className={
      "inline-flex h-9 items-center rounded-sm border px-4 text-xs font-medium transition-all duration-200 ease-out-quint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 active:scale-[0.97] " +
      (selected
        ? "border-ink bg-ink text-bone shadow-soft-1"
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
      // In light mode, soft shadow + lift on hover.
      // In dark mode, the bone background flips to near-black; cards use
      // the slightly-lighter --surface-elevated and gain a subtle tan glow
      // on hover (Resend-style halo).
      className="group relative flex h-full min-h-[280px] flex-col rounded-md border hairline bg-bone p-6 shadow-soft-1 transition-all duration-300 ease-out-quint hover:-translate-y-0.5 hover:border-tan hover:shadow-soft-3 dark:bg-[var(--surface-elevated)] dark:shadow-none dark:hover:shadow-[var(--glow-tan)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
    >
      {/* Top row — icon + install count. */}
      <div className="flex items-start justify-between gap-3">
        <span
          className="text-5xl leading-none transition-transform duration-300 ease-out-quint group-hover:-rotate-3 group-hover:scale-105"
          aria-hidden
        >
          {agent.icon_emoji}
        </span>
        <span className="flex items-baseline gap-1.5 font-mono text-[10px] uppercase tracking-eyebrow text-fg-muted">
          <span className="tabular-nums text-tan-text">
            {formatInstallCount(agent.install_count)}
          </span>
          <span>installs</span>
        </span>
      </div>

      {/* Name. */}
      <h3 className="mt-5 font-styrene text-xl font-bold leading-tight">
        {agent.name}
      </h3>

      {/* Description. */}
      <p className="mt-2 text-sm leading-relaxed text-fg-muted line-clamp-3">
        {agent.description}
      </p>

      {/* Footer — push to bottom via flex-1 spacer. */}
      <div className="mt-auto pt-5">
        <div className="flex items-center justify-between gap-3 border-t hairline pt-3 font-mono text-[10px]">
          <span className="uppercase tracking-eyebrow text-tan-text">
            {CATEGORY_LABELS[agent.category] ?? agent.category}
          </span>
          <span className="text-fg-muted">{agent.author}</span>
        </div>
      </div>

      {/* Subtle tan accent that fades in on hover — premium "active" cue. */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-x-6 top-0 h-px bg-tan opacity-0 transition-opacity duration-300 ease-out-quint group-hover:opacity-60"
      />
    </Link>
  </li>
);

const SkeletonGrid = () => (
  <ul
    className="grid gap-5 md:grid-cols-2 xl:grid-cols-3"
    aria-busy
    aria-label="Loading agents"
  >
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <li
        key={i}
        className="h-[280px] rounded-md border hairline bg-bone p-6 shadow-soft-1"
      >
        <div className="flex h-full flex-col gap-4">
          <div className="flex items-start justify-between">
            <div className="h-10 w-10 animate-shimmer rounded-sm" />
            <div className="h-3 w-20 animate-shimmer rounded-sm" />
          </div>
          <div className="space-y-2">
            <div className="h-5 w-3/4 animate-shimmer rounded-sm" />
            <div className="h-3 w-full animate-shimmer rounded-sm" />
            <div className="h-3 w-5/6 animate-shimmer rounded-sm" />
          </div>
          <div className="mt-auto border-t hairline pt-3">
            <div className="flex justify-between">
              <div className="h-2 w-24 animate-shimmer rounded-sm" />
              <div className="h-2 w-16 animate-shimmer rounded-sm" />
            </div>
          </div>
        </div>
      </li>
    ))}
  </ul>
);

const EmptyState = () => (
  <div className="rounded-md border hairline bg-bone p-12 text-center shadow-soft-1">
    <Eyebrow>No matches</Eyebrow>
    <h2 className="mt-3 font-styrene text-2xl font-bold">
      No agents in this category yet<span className="tan-period">.</span>
    </h2>
    <p className="mx-auto mt-2 max-w-md text-sm text-fg-muted">
      We're seeding more agents across the funnel. Switch to All to see
      everything that's available right now.
    </p>
  </div>
);
