"use client";

import { Eyebrow, Hairline, StatusPill, type StatusPillTone } from "@offside/ui";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";

import {
  type AutomationStepRun,
  type AutomationRun,
  type RunStatus,
  useAutomation,
  useAutomationRun,
  useCancelAutomationRun,
} from "../../../../../../lib/api";
import { useActiveWorkspace } from "../../../../../../lib/contexts";

const RUN_STATUS_TONE: Record<RunStatus, StatusPillTone> = {
  pending: "neutral",
  running: "info",
  awaiting_approval: "warning",
  awaiting_delay: "warning",
  awaiting_event: "warning",
  completed: "success",
  failed: "danger",
  cancelled: "neutral",
};

const STEP_STATUS_TONE: Record<AutomationStepRun["status"], StatusPillTone> = {
  pending: "neutral",
  running: "info",
  completed: "success",
  failed: "danger",
};

const TERMINAL: Set<RunStatus> = new Set(["completed", "failed", "cancelled"]);
const PARKED: Set<RunStatus> = new Set([
  "awaiting_approval",
  "awaiting_delay",
  "awaiting_event",
]);

export default function AutomationRunInspectorPage() {
  const { active } = useActiveWorkspace();
  const params = useParams<{ workspace: string; id: string; runId: string }>();
  if (!active) return null;
  return (
    <RunInspector
      workspaceId={active.id}
      workspaceSlug={active.slug}
      automationId={params.id}
      runId={params.runId}
    />
  );
}

const RunInspector = ({
  workspaceId,
  workspaceSlug,
  automationId,
  runId,
}: {
  workspaceId: number;
  workspaceSlug: string;
  automationId: string;
  runId: string;
}) => {
  const auto = useAutomation(workspaceId, automationId);
  // Poll while the run is non-terminal so the inspector "feels live"
  // — TanStack Query handles polling via refetchInterval, but our hook
  // doesn't accept one. We just refetch on focus/mount plus a manual
  // refresh button.
  const run = useAutomationRun(workspaceId, runId);
  const cancel = useCancelAutomationRun(workspaceId);
  const [cancelErr, setCancelErr] = React.useState<string | null>(null);

  // Light polling for in-flight runs.
  React.useEffect(() => {
    const status = run.data?.status;
    if (!status || TERMINAL.has(status)) return;
    const interval = window.setInterval(() => {
      run.refetch();
    }, 3000);
    return () => window.clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run.data?.status]);

  if (run.isLoading) {
    return <div className="px-6 py-8 text-fg-muted">Loading run…</div>;
  }
  const r = run.data;
  if (!r) {
    return (
      <div className="px-6 py-8">
        <p className="text-fg-muted">Run not found.</p>
        <Link
          href={`/${workspaceSlug}/automations/${automationId}`}
          className="mt-2 inline-block text-tan-text underline"
        >
          ← Back to workflow
        </Link>
      </div>
    );
  }

  const tone = RUN_STATUS_TONE[r.status] ?? "neutral";
  const automationName = auto.data?.name ?? `Automation #${automationId}`;
  const canCancel = !TERMINAL.has(r.status);
  const steps = r.step_runs ?? [];
  const totalCostCents = steps.reduce((sum, s) => sum + (s.cost_cents ?? 0), 0);

  const onCancel = async () => {
    setCancelErr(null);
    try {
      await cancel.mutateAsync(r.id);
    } catch (err) {
      setCancelErr(err instanceof Error ? err.message : "Cancel failed");
    }
  };

  return (
    <div className="space-y-6 px-6 py-8">
      <header className="flex items-end justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <Link
              href={`/${workspaceSlug}/automations/${automationId}`}
              className="font-mono text-[10px] uppercase tracking-eyebrow text-tan-text hover:underline"
            >
              ← {automationName}
            </Link>
            <StatusPill tone={tone}>{r.status.replace("_", " ")}</StatusPill>
            {r.version ? (
              <span className="font-mono text-[10px] text-fg-muted">
                version #{r.version}
              </span>
            ) : null}
          </div>
          <h1 className="mt-2 text-3xl font-styrene font-bold tracking-tight">
            Run #{r.id}<span className="tan-period">.</span>
          </h1>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => run.refetch()}
            className="inline-flex h-9 items-center rounded-sm border hairline bg-bone px-3 text-sm font-medium hover:border-tan"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={onCancel}
            disabled={!canCancel || cancel.isPending}
            className="inline-flex h-9 items-center rounded-sm border border-ink bg-ink px-3 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
          >
            {cancel.isPending ? "Cancelling…" : "Cancel run"}
          </button>
        </div>
      </header>

      {cancelErr ? (
        <p className="font-mono text-[11px] text-[#8E3B30]">{cancelErr}</p>
      ) : null}

      <Hairline />

      <RunMetadata run={r} totalCostCents={totalCostCents} />

      <section>
        <div className="flex items-end justify-between gap-3">
          <Eyebrow>Step runs · {steps.length}</Eyebrow>
          {PARKED.has(r.status) && r.resume_at ? (
            <span className="font-mono text-[10px] text-fg-muted">
              resume at {new Date(r.resume_at).toLocaleString()}
            </span>
          ) : null}
        </div>

        {steps.length === 0 ? (
          <p className="mt-3 text-sm text-fg-muted">
            No step runs recorded yet.
          </p>
        ) : (
          <ol className="mt-3 space-y-2">
            {steps.map((s) => (
              <StepRunRow key={s.id} step={s} isCurrent={s.step_id === r.current_step_id} />
            ))}
          </ol>
        )}
      </section>

      <section>
        <Eyebrow>State snapshot</Eyebrow>
        <p className="mt-1 font-mono text-[10px] text-fg-muted">
          Per-node outputs accumulated so far. Available to downstream{" "}
          {"{{ <node_id>.<field> }}"} templates.
        </p>
        <JsonBlock value={r.state_snapshot ?? {}} />
      </section>

      <section>
        <Eyebrow>Trigger payload</Eyebrow>
        <JsonBlock value={r.trigger_payload} />
      </section>
    </div>
  );
};

const RunMetadata = ({
  run,
  totalCostCents,
}: {
  run: AutomationRun;
  totalCostCents: number;
}) => (
  <dl className="grid grid-cols-2 gap-x-6 gap-y-3 font-mono text-[10px] text-fg-muted md:grid-cols-4">
    <Stat label="Started" value={fmtDate(run.started_at)} />
    <Stat label="Finished" value={fmtDate(run.finished_at)} />
    <Stat label="Current step" value={run.current_step_id || "—"} />
    <Stat label="Total cost" value={fmtCost(totalCostCents)} />
  </dl>
);

const Stat = ({ label, value }: { label: string; value: string }) => (
  <div>
    <dt className="uppercase tracking-eyebrow">{label}</dt>
    <dd className="mt-0.5 text-ink">{value}</dd>
  </div>
);

const fmtDate = (s: string | null) => (s ? new Date(s).toLocaleString() : "—");

const fmtCost = (cents: number) => {
  if (!cents) return "$0.00";
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: cents < 100 ? 4 : 2,
  }).format(cents / 100);
};

const StepRunRow = ({
  step,
  isCurrent,
}: {
  step: AutomationStepRun;
  isCurrent: boolean;
}) => {
  const tone = STEP_STATUS_TONE[step.status] ?? "neutral";
  return (
    <li
      className={
        "rounded-sm border hairline bg-bone shadow-soft-1 " +
        (isCurrent ? "ring-1 ring-tan" : "")
      }
    >
      <header className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="font-styrene text-sm font-bold">{step.step_id}</span>
          <span className="font-mono text-[10px] text-fg-muted">
            attempt {step.attempt}
          </span>
          <StatusPill tone={tone}>{step.status}</StatusPill>
          {isCurrent ? (
            <span className="rounded-sm border border-tan px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-eyebrow text-tan-text">
              current
            </span>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] text-fg-muted">
          <span>started {fmtDate(step.started_at)}</span>
          {step.finished_at ? <span>finished {fmtDate(step.finished_at)}</span> : null}
          {step.model ? <span>model {step.model}</span> : null}
          <span>cost {step.cost_cents}¢</span>
        </div>
      </header>
      <div className="border-t hairline px-4 py-3 space-y-2">
        <div className="font-mono text-[10px] text-fg-muted">
          idempotency_key · <span className="text-ink">{step.idempotency_key}</span>
        </div>
        <JsonBlock label="input" value={step.input} />
        <JsonBlock label="output" value={step.output} />
        {step.error ? <JsonBlock label="error" value={step.error} /> : null}
      </div>
    </li>
  );
};

const JsonBlock = ({ label, value }: { label?: string; value: unknown }) => (
  <details className="rounded-sm border hairline bg-bone">
    <summary className="cursor-pointer px-3 py-1.5 font-mono text-[10px] uppercase tracking-eyebrow text-tan-text">
      {label ?? "JSON"}
    </summary>
    <pre className="max-h-80 overflow-auto border-t hairline px-3 py-2 font-mono text-[10px] leading-relaxed text-ink/80">
      {safeStringify(value)}
    </pre>
  </details>
);

const safeStringify = (v: unknown) => {
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
};
