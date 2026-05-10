"use client";

import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  closestCorners,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import * as React from "react";

import {
  type Deal,
  type Pipeline,
  type PipelineStage,
  useDeals,
  usePipelines,
  useUpdateDeal,
} from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

const formatCurrency = (cents: number, currency: string) => {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(cents / 100);
  } catch {
    return `${currency} ${(cents / 100).toFixed(0)}`;
  }
};

export default function DealsKanbanPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <DealsKanban workspaceId={active.id} workspaceSlug={active.slug} />;
}

const DealsKanban = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const pipelines = usePipelines(workspaceId);
  const deals = useDeals(workspaceId);
  const updateDeal = useUpdateDeal(workspaceId);
  const [activePipelineId, setActivePipelineId] = React.useState<number | null>(null);
  const [activeDeal, setActiveDeal] = React.useState<Deal | null>(null);

  const pipelineList = pipelines.data?.results ?? [];
  const dealList = deals.data?.results ?? [];

  React.useEffect(() => {
    if (activePipelineId) return;
    const first = pipelineList.find((p) => p.is_default) ?? pipelineList[0];
    if (first) setActivePipelineId(first.id);
  }, [pipelineList, activePipelineId]);

  const pipeline = pipelineList.find((p) => p.id === activePipelineId) ?? null;
  const dealsByStage = React.useMemo(() => {
    const grouped = new Map<string, Deal[]>();
    if (!pipeline) return grouped;
    for (const stage of pipeline.stages) grouped.set(stage.id, []);
    for (const deal of dealList) {
      if (deal.pipeline !== pipeline.id) continue;
      const bucket = grouped.get(deal.stage_id);
      if (bucket) bucket.push(deal);
    }
    return grouped;
  }, [pipeline, dealList]);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }));

  const onDragStart = (event: DragStartEvent) => {
    const id = event.active.id as number;
    const found = dealList.find((d) => d.id === id) ?? null;
    setActiveDeal(found);
  };

  const onDragEnd = (event: DragEndEvent) => {
    setActiveDeal(null);
    const { active: dragging, over } = event;
    if (!over || !pipeline) return;
    const dealId = Number(dragging.id);
    const newStageId = String(over.id);
    const deal = dealList.find((d) => d.id === dealId);
    if (!deal || deal.stage_id === newStageId) return;
    if (!pipeline.stages.find((s) => s.id === newStageId)) return;
    updateDeal.mutate({ id: dealId, patch: { stage_id: newStageId } });
  };

  return (
    <div className="space-y-6 px-6 py-8">
      <header className="flex items-end justify-between gap-4">
        <div>
          <Eyebrow>Records</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            Deals<span className="tan-period">.</span>
          </h1>
        </div>
        <div className="flex items-end gap-3">
          <PipelinePicker
            pipelines={pipelineList}
            activeId={activePipelineId}
            onChange={setActivePipelineId}
          />
          <Link
            href={`/${workspaceSlug}/deals/new`}
            className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          >
            + New deal
          </Link>
        </div>
      </header>

      <Hairline />

      {!pipeline ? (
        <p className="text-fg-muted">Loading pipeline…</p>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
        >
          <div className="flex gap-3 overflow-x-auto pb-4">
            {pipeline.stages
              .slice()
              .sort((a, b) => a.order - b.order)
              .map((stage) => (
                <KanbanColumn
                  key={stage.id}
                  stage={stage}
                  deals={dealsByStage.get(stage.id) ?? []}
                  workspaceSlug={workspaceSlug}
                />
              ))}
          </div>

          <DragOverlay>
            {activeDeal ? (
              <DealCardSurface deal={activeDeal} workspaceSlug={workspaceSlug} dragging />
            ) : null}
          </DragOverlay>
        </DndContext>
      )}
    </div>
  );
};

const PipelinePicker = ({
  pipelines,
  activeId,
  onChange,
}: {
  pipelines: Pipeline[];
  activeId: number | null;
  onChange: (id: number) => void;
}) => (
  <div>
    <label htmlFor="pipeline-picker" className="text-xs font-medium text-fg-muted">
      Pipeline
    </label>
    <select
      id="pipeline-picker"
      value={activeId ?? ""}
      onChange={(e) => onChange(Number(e.target.value))}
      className="mt-1 block rounded-sm border hairline bg-bone px-3 py-2 text-sm"
    >
      {pipelines.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name}
          {p.is_default ? " (default)" : ""}
        </option>
      ))}
    </select>
  </div>
);

const KanbanColumn = ({
  stage,
  deals,
  workspaceSlug,
}: {
  stage: PipelineStage;
  deals: Deal[];
  workspaceSlug: string;
}) => {
  const { setNodeRef, isOver } = useDroppable({ id: stage.id });
  const totalCents = deals.reduce((sum, d) => sum + d.value_cents, 0);
  const currency = deals[0]?.currency ?? "USD";

  return (
    <section
      ref={setNodeRef}
      aria-label={stage.label}
      className={
        "flex w-[300px] shrink-0 flex-col rounded-md border hairline bg-bone transition-colors " +
        (isOver ? "ring-2 ring-tan" : "")
      }
    >
      <header className="border-b hairline px-3 py-2">
        <div className="flex items-center justify-between gap-2">
          <span className="font-styrene text-xs font-bold uppercase tracking-eyebrow text-tan-text">
            {stage.label}
          </span>
          <span className="font-mono text-[10px] text-fg-muted">{deals.length}</span>
        </div>
        {totalCents > 0 ? (
          <p className="mt-0.5 font-mono text-[10px] text-fg-muted">
            {formatCurrency(totalCents, currency)}
          </p>
        ) : null}
      </header>
      <div className="flex-1 space-y-2 overflow-y-auto p-2">
        {deals.length === 0 ? (
          <p className="px-2 py-4 text-center text-xs text-fg-muted">No deals</p>
        ) : (
          deals.map((deal) => (
            <DraggableDealCard key={deal.id} deal={deal} workspaceSlug={workspaceSlug} />
          ))
        )}
      </div>
    </section>
  );
};

const DraggableDealCard = ({
  deal,
  workspaceSlug,
}: {
  deal: Deal;
  workspaceSlug: string;
}) => {
  const { setNodeRef, attributes, listeners, isDragging } = useDraggable({ id: deal.id });
  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      style={{ opacity: isDragging ? 0.4 : 1 }}
      className="cursor-grab active:cursor-grabbing"
    >
      <DealCardSurface deal={deal} workspaceSlug={workspaceSlug} />
    </div>
  );
};

const DealCardSurface = ({
  deal,
  workspaceSlug,
  dragging = false,
}: {
  deal: Deal;
  workspaceSlug: string;
  dragging?: boolean;
}) => (
  <article
    className={
      "rounded-sm border hairline bg-bone p-3 shadow-soft-1 " +
      (dragging ? "rotate-1 shadow-soft-3" : "")
    }
  >
    <Link
      href={`/${workspaceSlug}/deals/${deal.id}`}
      onClick={(e) => e.stopPropagation()}
      className="block hover:text-tan-text"
    >
      <p className="text-sm font-medium">{deal.name}</p>
    </Link>
    <p className="mt-1 font-mono text-[11px] text-fg-muted">
      {formatCurrency(deal.value_cents, deal.currency)}
    </p>
    {deal.expected_close ? (
      <div className="mt-2">
        <StatusPill tone="neutral">
          close {new Date(deal.expected_close).toLocaleDateString()}
        </StatusPill>
      </div>
    ) : null}
  </article>
);
