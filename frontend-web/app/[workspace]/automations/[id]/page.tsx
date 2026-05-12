"use client";

import { Eyebrow, Hairline, StatusPill, type StatusPillTone } from "@offside/ui";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";

import {
  type AutomationGraph,
  type AutomationStatus,
  useAutomation,
  useAutomationRuns,
  useAutomationVersions,
  usePublishAutomation,
  useStartAutomationRun,
  useUpdateAutomation,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { validateGraph } from "../../../../lib/workflow-graph";

import { WorkflowCanvas } from "../../../../components/workflow-canvas";

const STATUS_TONE: Record<AutomationStatus, StatusPillTone> = {
  draft: "neutral",
  active: "success",
  paused: "warning",
  archived: "neutral",
};

export default function AutomationEditorPage() {
  const { active } = useActiveWorkspace();
  const params = useParams<{ workspace: string; id: string }>();
  if (!active) return null;
  return (
    <AutomationEditor
      workspaceId={active.id}
      workspaceSlug={active.slug}
      automationId={params.id}
    />
  );
}

const AutomationEditor = ({
  workspaceId,
  workspaceSlug,
  automationId,
}: {
  workspaceId: number;
  workspaceSlug: string;
  automationId: string;
}) => {
  const auto = useAutomation(workspaceId, automationId);
  const versions = useAutomationVersions(workspaceId, automationId);
  const runs = useAutomationRuns(workspaceId, automationId);
  const update = useUpdateAutomation(workspaceId);
  const publish = usePublishAutomation(workspaceId);
  const startRun = useStartAutomationRun(workspaceId);

  const automation = auto.data;
  const [draftName, setDraftName] = React.useState<string>("");
  const [saveState, setSaveState] = React.useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (automation && draftName === "") setDraftName(automation.name);
    // Only seed once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [automation?.id]);

  const onGraphChange = React.useCallback(
    async (graph: AutomationGraph) => {
      if (!automation) return;
      try {
        setSaveState("saving");
        await update.mutateAsync({ id: automation.id, patch: { graph } });
        setSaveState("saved");
      } catch (err) {
        setSaveState("error");
        setErrorMsg(err instanceof Error ? err.message : String(err));
      }
    },
    [automation, update],
  );

  const onRenameBlur = async () => {
    if (!automation || draftName === automation.name) return;
    await update.mutateAsync({ id: automation.id, patch: { name: draftName.trim() || "Untitled workflow" } });
  };

  const onPublish = async () => {
    if (!automation) return;
    setErrorMsg(null);
    try {
      await publish.mutateAsync(automation.id);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Publish failed");
    }
  };

  const onRun = async () => {
    if (!automation) return;
    setErrorMsg(null);
    try {
      await startRun.mutateAsync({ id: automation.id });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Run failed");
    }
  };

  if (auto.isLoading) {
    return (
      <div className="px-6 py-8 text-fg-muted">Loading workflow…</div>
    );
  }
  if (!automation) {
    return (
      <div className="px-6 py-8">
        <p className="text-fg-muted">Workflow not found.</p>
        <Link href={`/${workspaceSlug}/automations`} className="mt-2 inline-block text-tan-text underline">
          ← Back to automations
        </Link>
      </div>
    );
  }

  const tone = STATUS_TONE[automation.status] ?? "neutral";
  const issues = validateGraph(automation.graph);
  const publishedNumber = automation.version;
  const runList = runs.data?.results ?? [];

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      <header className="border-b hairline bg-bone px-6 py-4">
        <div className="flex items-end justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3">
              <Link
                href={`/${workspaceSlug}/automations`}
                className="font-mono text-[10px] uppercase tracking-eyebrow text-tan-text hover:underline"
              >
                ← Automations
              </Link>
              <StatusPill tone={tone}>{automation.status}</StatusPill>
              <span className="font-mono text-[10px] text-fg-muted">
                v{publishedNumber}
              </span>
            </div>
            <input
              type="text"
              value={draftName}
              onChange={(e) => setDraftName(e.target.value)}
              onBlur={onRenameBlur}
              className="mt-2 w-full max-w-2xl border-none bg-transparent text-3xl font-styrene font-bold tracking-tight outline-none focus:ring-0"
              aria-label="Workflow name"
            />
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <SaveIndicator state={saveState} />
            <button
              type="button"
              onClick={onRun}
              disabled={startRun.isPending || !automation.published_version}
              title={
                automation.published_version
                  ? "Run this workflow now"
                  : "Publish a version first"
              }
              className="inline-flex h-9 items-center rounded-sm border hairline bg-bone px-3 text-sm font-medium hover:border-tan focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan disabled:opacity-50"
            >
              {startRun.isPending ? "Running…" : "Run"}
            </button>
            <button
              type="button"
              onClick={onPublish}
              disabled={publish.isPending || issues.length > 0}
              title={issues.length > 0 ? `Resolve ${issues.length} validation issue(s) first` : "Snapshot draft → version"}
              className="inline-flex h-9 items-center rounded-sm border border-ink bg-ink px-3 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2 disabled:opacity-50"
            >
              {publish.isPending ? "Publishing…" : "Publish"}
            </button>
          </div>
        </div>

        {errorMsg ? (
          <p className="mt-2 font-mono text-[11px] text-[#8E3B30]">{errorMsg}</p>
        ) : null}
      </header>

      <WorkflowCanvas graph={automation.graph} onChange={onGraphChange} />

      <footer className="border-t hairline bg-bone px-6 py-3">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <span className="font-mono text-[10px] text-fg-muted">
            Versions ·{" "}
            <span className="text-ink">{versions.data?.results?.length ?? 0}</span>
          </span>
          <span className="font-mono text-[10px] text-fg-muted">
            Runs · <span className="text-ink">{runList.length}</span>
          </span>
          {runList.slice(0, 5).map((r) => (
            <Link
              key={r.id}
              href={`/${workspaceSlug}/automations/${automation.id}/runs/${r.id}`}
              className="rounded-sm border hairline bg-bone px-2 py-0.5 font-mono text-[10px] hover:border-tan"
            >
              <span className="text-fg-muted">#{r.id}</span>{" "}
              <span className="text-ink">{r.status}</span>
            </Link>
          ))}
        </div>
      </footer>

      <Hairline />
    </div>
  );
};

const SaveIndicator = ({ state }: { state: "idle" | "saving" | "saved" | "error" }) => {
  const dotClass =
    state === "saving"
      ? "bg-tan animate-pulse"
      : state === "saved"
        ? "bg-[#3B6A4A]"
        : state === "error"
          ? "bg-[#8E3B30]"
          : "bg-fg-muted/40";
  const label =
    state === "saving"
      ? "saving…"
      : state === "saved"
        ? "saved"
        : state === "error"
          ? "save failed"
          : "draft";
  return (
    <span className="flex items-center gap-1.5 font-mono text-[10px] text-fg-muted">
      <span className={"h-1.5 w-1.5 rounded-full " + dotClass} />
      {label}
    </span>
  );
};
