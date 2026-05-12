"use client";

import { Eyebrow } from "@offside/ui";
import * as React from "react";

import type { AutomationNodeType } from "../lib/api";
import { NODE_TYPES, labelFor } from "../lib/workflow-graph";

const DESCRIPTIONS: Record<AutomationNodeType, string> = {
  action: "Run a side effect (CRM mutate, AI, HTTP).",
  branch: "Route based on a field comparison.",
  delay: "Wait a fixed duration before continuing.",
  approval: "Pause for human approval via HITL.",
  wait_for_event: "Park until a named event fires.",
  end: "Terminate the run.",
};

interface Props {
  readOnly?: boolean;
  onAdd: (type: AutomationNodeType, clientX?: number, clientY?: number) => void;
}

export const WorkflowNodePalette = ({ readOnly = false, onAdd }: Props) => (
  <aside aria-label="Node palette" className="border-r hairline bg-bone p-3">
    <Eyebrow>Nodes</Eyebrow>
    <p className="mt-1 font-mono text-[10px] text-fg-muted">
      Drag onto canvas
    </p>

    <ul className="mt-3 space-y-1.5">
      {NODE_TYPES.map((type) => (
        <li key={type}>
          <button
            type="button"
            disabled={readOnly}
            onClick={() => onAdd(type)}
            draggable={!readOnly}
            onDragStart={(e) => {
              e.dataTransfer.setData("application/automation-node", type);
              e.dataTransfer.effectAllowed = "move";
            }}
            className="group flex w-full cursor-grab flex-col gap-0.5 rounded-sm border hairline bg-bone px-2.5 py-2 text-left transition-colors hover:border-tan hover:bg-tan-100 active:cursor-grabbing disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span className="font-styrene text-[10px] font-bold uppercase tracking-eyebrow text-tan-text">
              {type.replace("_", " ")}
            </span>
            <span className="text-sm font-medium">{labelFor(type)}</span>
            <span className="text-[11px] text-fg-muted">{DESCRIPTIONS[type]}</span>
          </button>
        </li>
      ))}
    </ul>
  </aside>
);
