"use client";

import { Eyebrow } from "@offside/ui";
import * as React from "react";

import { type Activity, type RelatedType, useActivitiesFor } from "../lib/api";
import { useActiveWorkspace } from "../lib/contexts";

interface Props {
  relatedType: RelatedType;
  relatedId: number;
}

const KIND_LABEL: Record<string, string> = {
  record_created: "created",
  record_updated: "updated",
  field_changed: "field changed",
  note_added: "note added",
  task_created: "task created",
  task_completed: "task completed",
  deal_stage_changed: "stage changed",
  email_sent: "email sent",
  email_received: "email received",
  ai_action: "AI action",
  automation_run: "automation",
};

export const ActivityFeed = ({ relatedType, relatedId }: Props) => {
  const { active } = useActiveWorkspace();
  const activities = useActivitiesFor(active?.id, relatedType, relatedId);

  if (activities.isLoading) {
    return <p className="text-fg-muted text-sm">Loading activity…</p>;
  }
  const list = activities.data?.results ?? [];
  if (list.length === 0) {
    return (
      <p className="text-fg-muted text-sm">No activity yet — actions and changes show up here.</p>
    );
  }

  return (
    <ol className="space-y-3">
      {list.map((a) => (
        <ActivityRow key={a.id} activity={a} />
      ))}
    </ol>
  );
};

const ActivityRow = ({ activity }: { activity: Activity }) => {
  const label = KIND_LABEL[activity.kind] ?? activity.kind;
  const actor = activity.actor_email ?? "system";
  const summary = describePayload(activity);
  return (
    <li className="flex gap-3 text-sm">
      <span className="mt-1 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-tan" aria-hidden />
      <div className="flex-1 space-y-0.5">
        <p>
          <span className="font-medium">{actor}</span>
          <span className="text-fg-muted"> · {label}</span>
          {summary ? <span className="text-fg-muted"> · {summary}</span> : null}
        </p>
        <p className="font-mono text-[11px] text-fg-muted">
          {new Date(activity.occurred_at).toLocaleString()}
        </p>
      </div>
    </li>
  );
};

const describePayload = (activity: Activity): string | null => {
  const p = activity.payload;
  if (!p || typeof p !== "object") return null;
  if (activity.kind === "deal_stage_changed" && typeof p.stage_id === "string") {
    return `→ ${p.stage_id}`;
  }
  if (activity.kind === "record_created" && typeof p.name === "string") {
    return p.name;
  }
  if (activity.kind === "record_created" && typeof p.primary_email === "string") {
    return p.primary_email;
  }
  return null;
};
