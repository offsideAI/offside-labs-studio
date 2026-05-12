"use client";

import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  useReactFlow,
  type Connection,
  type EdgeChange,
  type NodeChange,
  type NodeProps,
} from "@xyflow/react";
import * as React from "react";

import type { AutomationGraph, AutomationNodeType } from "../lib/api";
import {
  type EditorEdge,
  type EditorNode,
  type EdgeKind,
  flowToGraph,
  generateNodeId,
  graphToFlow,
  labelFor,
  nodePreset,
  validateGraph,
  type ValidationIssue,
} from "../lib/workflow-graph";

import { WorkflowNodeDrawer } from "./workflow-node-drawer";
import { WorkflowNodePalette } from "./workflow-node-palette";

interface WorkflowCanvasProps {
  graph: AutomationGraph;
  readOnly?: boolean;
  onChange: (next: AutomationGraph) => void;
}

export const WorkflowCanvas = (props: WorkflowCanvasProps) => (
  <ReactFlowProvider>
    <WorkflowCanvasInner {...props} />
  </ReactFlowProvider>
);

const WorkflowCanvasInner = ({ graph, readOnly = false, onChange }: WorkflowCanvasProps) => {
  const flow = useReactFlow();
  const initial = React.useMemo(() => graphToFlow(graph), [graph]);
  const [nodes, setNodes] = React.useState<EditorNode[]>(initial.nodes);
  const [edges, setEdges] = React.useState<EditorEdge[]>(initial.edges);
  const [selectedId, setSelectedId] = React.useState<string | null>(null);

  // Re-seed from incoming graph when it changes from outside (e.g. NL→graph
  // hydration in M8.S3). Skip if the hash matches our serialized state so
  // local edits don't get clobbered by our own optimistic patches.
  const graphHashRef = React.useRef<string>("");
  React.useEffect(() => {
    const incoming = JSON.stringify(graph);
    if (incoming === graphHashRef.current) return;
    graphHashRef.current = incoming;
    const fresh = graphToFlow(graph);
    setNodes(fresh.nodes);
    setEdges(fresh.edges);
  }, [graph]);

  // Push edits up. Debounced to avoid spamming the autosave PATCH.
  const onChangeRef = React.useRef(onChange);
  onChangeRef.current = onChange;
  React.useEffect(() => {
    const handle = setTimeout(() => {
      const next = flowToGraph(graph, nodes, edges);
      const serialized = JSON.stringify(next);
      if (serialized === graphHashRef.current) return;
      graphHashRef.current = serialized;
      onChangeRef.current(next);
    }, 300);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, edges]);

  const handleNodesChange = React.useCallback(
    (changes: NodeChange[]) => setNodes((ns) => applyNodeChanges(changes, ns) as EditorNode[]),
    [],
  );
  const handleEdgesChange = React.useCallback(
    (changes: EdgeChange[]) => setEdges((es) => applyEdgeChanges(changes, es) as EditorEdge[]),
    [],
  );
  const handleConnect = React.useCallback((connection: Connection) => {
    const kind = (connection.sourceHandle as EdgeKind | null) ?? "next";
    setEdges((es) => {
      // For non-branch/approval source handles we only allow one outgoing
      // edge per source; replace any existing one of the same kind.
      const filtered = es.filter(
        (e) => !(e.source === connection.source && (e.data?.kind ?? "next") === kind),
      );
      return addEdge<EditorEdge>(
        {
          ...connection,
          id: `${connection.source}->${connection.target}:${kind}`,
          markerEnd: { type: MarkerType.ArrowClosed, color: "#7A5F44" },
          label: kind === "next" ? undefined : kind,
          data: { kind },
        },
        filtered,
      );
    });
  }, []);

  const addNodeFromPalette = React.useCallback(
    (type: AutomationNodeType, clientX?: number, clientY?: number) => {
      if (readOnly) return;
      setNodes((ns) => {
        const existingIds = Object.fromEntries(ns.map((n) => [n.id, true]));
        const id = generateNodeId(existingIds);
        const preset = nodePreset(type);
        const position =
          clientX != null && clientY != null
            ? flow.screenToFlowPosition({ x: clientX, y: clientY })
            : { x: 100 + ns.length * 40, y: 100 + ns.length * 40 };
        const isFirst = ns.length === 0;
        const node: EditorNode = {
          id,
          type: "automation",
          position,
          data: {
            nodeId: id,
            nodeType: type,
            label: preset.label,
            config: { ...preset.config },
            isStart: isFirst,
          },
        };
        return [...ns, node];
      });
    },
    [readOnly, flow],
  );

  const onPaneClick = React.useCallback(() => setSelectedId(null), []);
  const onNodeClick = React.useCallback((_: unknown, n: EditorNode) => setSelectedId(n.id), []);
  const onNodeDelete = React.useCallback(
    (id: string) => {
      setNodes((ns) => ns.filter((n) => n.id !== id));
      setEdges((es) => es.filter((e) => e.source !== id && e.target !== id));
      setSelectedId((cur) => (cur === id ? null : cur));
    },
    [],
  );

  const updateNode = React.useCallback(
    (id: string, patch: Partial<EditorNode["data"]>) => {
      setNodes((ns) =>
        ns.map((n) => (n.id === id ? { ...n, data: { ...n.data, ...patch } } : n)),
      );
    },
    [],
  );

  const setAsStart = React.useCallback((id: string) => {
    setNodes((ns) =>
      ns.map((n) => ({ ...n, data: { ...n.data, isStart: n.id === id } })),
    );
  }, []);

  // Validation runs over the snapshot we're about to push up.
  const liveGraph = React.useMemo(() => flowToGraph(graph, nodes, edges), [graph, nodes, edges]);
  const issues = React.useMemo<ValidationIssue[]>(() => validateGraph(liveGraph), [liveGraph]);

  const selected = nodes.find((n) => n.id === selectedId) ?? null;

  // Drag-and-drop from palette.
  const onDragOver = React.useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);
  const onDrop = React.useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData("application/automation-node");
      if (!type) return;
      addNodeFromPalette(type as AutomationNodeType, event.clientX, event.clientY);
    },
    [addNodeFromPalette],
  );

  return (
    <div className="grid grid-cols-[200px_minmax(0,1fr)_320px] gap-0 border-y hairline">
      <WorkflowNodePalette readOnly={readOnly} onAdd={addNodeFromPalette} />

      <div className="relative h-[calc(100vh-220px)] min-h-[480px] bg-bone" onDragOver={onDragOver} onDrop={onDrop}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={handleConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={NODE_TYPES_MAP}
          nodesDraggable={!readOnly}
          nodesConnectable={!readOnly}
          edgesReconnectable={!readOnly}
          deleteKeyCode={readOnly ? null : ["Delete", "Backspace"]}
          proOptions={{ hideAttribution: true }}
          fitView
        >
          <Background variant={BackgroundVariant.Dots} gap={18} size={1} color="#E1D8CC" />
          <MiniMap pannable zoomable className="!border !hairline !bg-bone" />
          <Controls position="bottom-left" className="!border !hairline !bg-bone !shadow-soft-1" />
        </ReactFlow>

        {issues.length > 0 && (
          <ValidationOverlay issues={issues} />
        )}
      </div>

      <WorkflowNodeDrawer
        readOnly={readOnly}
        node={selected}
        onChange={(patch) => selected && updateNode(selected.id, patch)}
        onDelete={() => selected && onNodeDelete(selected.id)}
        onSetStart={() => selected && setAsStart(selected.id)}
      />
    </div>
  );
};

const ValidationOverlay = ({ issues }: { issues: ValidationIssue[] }) => (
  <div className="pointer-events-none absolute bottom-3 left-3 right-3 z-10">
    <div className="pointer-events-auto max-h-32 overflow-y-auto rounded-sm border hairline bg-bone/95 px-3 py-2 shadow-soft-2 backdrop-blur">
      <p className="font-styrene text-[10px] font-bold uppercase tracking-eyebrow text-tan-text">
        Validation · {issues.length} {issues.length === 1 ? "issue" : "issues"}
      </p>
      <ul className="mt-1 space-y-0.5 font-mono text-[11px] text-ink/80">
        {issues.slice(0, 6).map((issue, i) => (
          <li key={i}>
            {issue.nodeId ? <span className="text-tan-text">{issue.nodeId}: </span> : null}
            {issue.message}
          </li>
        ))}
        {issues.length > 6 ? (
          <li className="text-fg-muted">+{issues.length - 6} more…</li>
        ) : null}
      </ul>
    </div>
  </div>
);

// --- Custom node ---

const NODE_TONE: Record<AutomationNodeType, string> = {
  action: "border-tan/60 bg-bone",
  delay: "border-ink/40 bg-bone",
  approval: "border-[#c98f89] bg-bone",
  branch: "border-tan/60 bg-bone",
  wait_for_event: "border-ink/40 bg-bone",
  end: "border-ink bg-ink text-bone",
};

const AutomationNodeView = ({ data, selected }: NodeProps) => {
  const { nodeType, label, isStart } = data as EditorNode["data"];
  const tone = NODE_TONE[nodeType] ?? NODE_TONE.action;
  return (
    <div
      className={
        "min-w-[160px] rounded-sm border-2 px-3 py-2 shadow-soft-1 transition-shadow " +
        tone +
        (selected ? " ring-2 ring-tan ring-offset-2 ring-offset-bone" : "")
      }
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-styrene text-[10px] font-bold uppercase tracking-eyebrow opacity-70">
          {nodeType.replace("_", " ")}
        </span>
        {isStart ? (
          <span className="rounded-sm border border-tan px-1.5 py-px font-mono text-[9px] uppercase tracking-eyebrow text-tan-text">
            start
          </span>
        ) : null}
      </div>
      <p className="mt-0.5 text-sm font-medium">{label || labelFor(nodeType)}</p>

      {/* Source handles. */}
      {nodeType === "branch" ? (
        <>
          <Handle
            id="true"
            type="source"
            position={Position.Right}
            style={{ top: "30%", background: "#7A5F44" }}
          />
          <Handle
            id="false"
            type="source"
            position={Position.Right}
            style={{ top: "70%", background: "#7A5F44" }}
          />
        </>
      ) : nodeType === "approval" ? (
        <>
          <Handle
            id="approve"
            type="source"
            position={Position.Right}
            style={{ top: "30%", background: "#7A5F44" }}
          />
          <Handle
            id="reject"
            type="source"
            position={Position.Right}
            style={{ top: "70%", background: "#7A5F44" }}
          />
        </>
      ) : nodeType === "end" ? null : (
        <Handle id="next" type="source" position={Position.Right} style={{ background: "#7A5F44" }} />
      )}

      {/* Target handle (everyone except the start can be a target; React Flow
          enforces nothing here — semantic enforcement is in validate()). */}
      <Handle type="target" position={Position.Left} style={{ background: "#7A5F44" }} />
    </div>
  );
};

const NODE_TYPES_MAP = { automation: AutomationNodeView };
