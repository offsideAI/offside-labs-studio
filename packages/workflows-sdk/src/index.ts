// @offside/workflows-sdk — typed event names and action client for the
// custom Django+Celery durable workflow runtime (PLAN.md §7).
//
// The real action HTTP client lands in M7 (Workflow runtime v0); the
// canvas authoring lands in M8.

export const EventName = {
  RecordCreated: "offside.record.created",
  RecordUpdated: "offside.record.updated",
  RecordFieldChanged: "offside.record.field_changed",
  RecordDeleted: "offside.record.deleted",
  WebhookReceived: "offside.webhook.received",
  FormSubmitted: "offside.form.submitted",
  GmailMessageReceived: "offside.gmail.message_received",
  HitlDecided: "offside.hitl.decided",
} as const;

export type EventName = (typeof EventName)[keyof typeof EventName];

export interface RecordEventPayload {
  workspace_id: string;
  entity_type: "contact" | "company" | "deal" | "task" | "note";
  entity_id: string;
  diff?: Record<string, { from: unknown; to: unknown }>;
}

export interface HitlDecisionPayload {
  run_id: string;
  step_id: string;
  decision: "approve" | "reject";
  decided_by: string;
}

// Stub — implemented in M7.
export interface ActionClient {
  invoke<TIn, TOut>(action: string, input: TIn, idempotencyKey: string): Promise<TOut>;
}
