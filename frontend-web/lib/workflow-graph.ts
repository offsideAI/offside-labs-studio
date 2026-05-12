// Conversion between the backend's AutomationGraph shape and the flat
// nodes[]/edges[] arrays React Flow expects. The backend is the source of
// truth — `position` is the only editor-only key we round-trip.

import type { Edge, Node } from "@xyflow/react";

import type { AutomationGraph, AutomationNode, AutomationNodeType } from "./api";

export type EditorNodeData = {
  nodeId: string;
  nodeType: AutomationNodeType;
  label: string;
  isStart: boolean;
  config: Record<string, unknown>;
};

export type EditorNode = Node<EditorNodeData>;
export type EditorEdge = Edge<{ kind: EdgeKind }>;

export type EdgeKind = "next" | "approve" | "reject" | "true" | "false";

const NODE_PRESETS: Record<AutomationNodeType, { label: string; config: Record<string, unknown> }> = {
  action: { label: "Action", config: { action: "noop", input: {} } },
  delay: { label: "Delay", config: { seconds: 60 } },
  approval: { label: "Approval", config: { summary: "Please approve" } },
  branch: { label: "Branch", config: { field: "", op: "eq", value: "" } },
  wait_for_event: { label: "Wait for event", config: { event_key: "" } },
  end: { label: "End", config: {} },
};

export const nodePreset = (type: AutomationNodeType) => NODE_PRESETS[type];

export const NODE_TYPES: AutomationNodeType[] = [
  "action",
  "branch",
  "delay",
  "approval",
  "wait_for_event",
  "end",
];

export const labelFor = (type: AutomationNodeType) => NODE_PRESETS[type].label;

export const graphToFlow = (
  graph: AutomationGraph,
): { nodes: EditorNode[]; edges: EditorEdge[] } => {
  const nodes: EditorNode[] = [];
  const edges: EditorEdge[] = [];
  const dict = graph.nodes ?? {};
  const startId = graph.start_node_id;

  Object.entries(dict).forEach(([id, raw]) => {
    const position = (raw.position as { x: number; y: number } | undefined) ?? {
      x: 0,
      y: 0,
    };
    nodes.push({
      id,
      type: "automation",
      position,
      data: {
        nodeId: id,
        nodeType: raw.type,
        label: typeof raw.label === "string" && raw.label.trim() ? raw.label : labelFor(raw.type),
        isStart: id === startId,
        config: (raw.config as Record<string, unknown>) ?? {},
      },
    });

    const push = (target: string | undefined, kind: EdgeKind, sourceHandle?: string) => {
      if (!target) return;
      edges.push({
        id: `${id}->${target}:${kind}`,
        source: id,
        target,
        sourceHandle,
        data: { kind },
        label: kind === "next" ? undefined : kind,
      });
    };

    if (raw.type === "branch") {
      push(raw.true_next, "true", "true");
      push(raw.false_next, "false", "false");
    } else if (raw.type === "approval") {
      push(raw.approve_next, "approve", "approve");
      push(raw.reject_next, "reject", "reject");
    } else {
      push(raw.next, "next");
    }
  });

  return { nodes, edges };
};

export const flowToGraph = (
  prev: AutomationGraph,
  nodes: EditorNode[],
  edges: EditorEdge[],
): AutomationGraph => {
  // Rebuild the nodes dict from the editor state. We preserve config/label
  // from React Flow node.data, positions from node.position, and recompute
  // next/approve_next/... from edges. start_node_id is whatever node has
  // data.isStart, falling back to the first node.
  const nodeDict: Record<string, AutomationNode> = {};
  let startId: string | undefined = prev.start_node_id;

  for (const n of nodes) {
    const { nodeType, label, config, isStart } = n.data;
    const base: AutomationNode = {
      type: nodeType,
      config,
      label,
      position: { x: n.position.x, y: n.position.y },
    };
    nodeDict[n.id] = base;
    if (isStart) startId = n.id;
  }

  for (const e of edges) {
    const src = nodeDict[e.source];
    if (!src) continue;
    const kind = (e.data?.kind ?? (e.sourceHandle as EdgeKind | undefined) ?? "next") as EdgeKind;
    if (src.type === "branch") {
      if (kind === "true") src.true_next = e.target;
      if (kind === "false") src.false_next = e.target;
    } else if (src.type === "approval") {
      if (kind === "approve") src.approve_next = e.target;
      if (kind === "reject") src.reject_next = e.target;
    } else {
      src.next = e.target;
    }
  }

  if (!startId && nodes.length > 0) startId = nodes[0]!.id;

  return { start_node_id: startId, nodes: nodeDict };
};

export const generateNodeId = (existing: Record<string, unknown> = {}): string => {
  for (let i = 1; i < 10_000; i++) {
    const id = `n${i}`;
    if (!(id in existing)) return id;
  }
  return `n${Date.now()}`;
};

export type ValidationIssue = { nodeId?: string; message: string };

export const validateGraph = (graph: AutomationGraph): ValidationIssue[] => {
  const issues: ValidationIssue[] = [];
  const dict = graph.nodes ?? {};
  const ids = Object.keys(dict);
  if (ids.length === 0) {
    issues.push({ message: "Graph is empty — add a node to start." });
    return issues;
  }
  if (!graph.start_node_id) {
    issues.push({ message: "No start node selected." });
  } else if (!dict[graph.start_node_id]) {
    issues.push({ message: `start_node_id "${graph.start_node_id}" is missing from nodes.` });
  }

  // Validate outgoing edges + per-type required config.
  for (const [id, n] of Object.entries(dict)) {
    const refs: Array<{ key: string; target: string | undefined }> = [];
    if (n.type === "branch") {
      refs.push({ key: "true_next", target: n.true_next });
      refs.push({ key: "false_next", target: n.false_next });
      if (!n.config || !(n.config as Record<string, unknown>).field) {
        issues.push({ nodeId: id, message: "branch node missing config.field" });
      }
    } else if (n.type === "approval") {
      refs.push({ key: "approve_next", target: n.approve_next });
      refs.push({ key: "reject_next", target: n.reject_next });
    } else if (n.type !== "end") {
      refs.push({ key: "next", target: n.next });
    }
    if (n.type === "action") {
      if (!(n.config as Record<string, unknown>)?.action) {
        issues.push({ nodeId: id, message: "action node missing config.action" });
      }
    }
    for (const ref of refs) {
      if (!ref.target) {
        if (n.type !== "end")
          issues.push({ nodeId: id, message: `node has no outgoing "${ref.key}" connection` });
        continue;
      }
      if (!dict[ref.target]) {
        issues.push({
          nodeId: id,
          message: `${ref.key} → "${ref.target}" points at a missing node`,
        });
      }
    }
  }

  // Reachability from start.
  if (graph.start_node_id && dict[graph.start_node_id]) {
    const reachable = new Set<string>();
    const stack = [graph.start_node_id];
    while (stack.length) {
      const cur = stack.pop()!;
      if (reachable.has(cur)) continue;
      reachable.add(cur);
      const n = dict[cur];
      if (!n) continue;
      for (const t of [n.next, n.approve_next, n.reject_next, n.true_next, n.false_next]) {
        if (t && dict[t]) stack.push(t);
      }
    }
    for (const id of ids) {
      if (!reachable.has(id)) {
        issues.push({ nodeId: id, message: "node is not reachable from start" });
      }
    }
  }

  return issues;
};
