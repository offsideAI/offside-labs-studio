"use client";

import { Eyebrow } from "@offside/ui";
import * as React from "react";

import type { AutomationNodeType } from "../lib/api";
import type { EditorNode } from "../lib/workflow-graph";

interface Props {
  node: EditorNode | null;
  readOnly?: boolean;
  onChange: (patch: Partial<EditorNode["data"]>) => void;
  onDelete: () => void;
  onSetStart: () => void;
}

const labelFieldId = "node-label";

export const WorkflowNodeDrawer = ({
  node,
  readOnly = false,
  onChange,
  onDelete,
  onSetStart,
}: Props) => {
  if (!node) {
    return (
      <aside
        aria-label="Node config"
        className="border-l hairline bg-bone p-4"
      >
        <Eyebrow>Inspector</Eyebrow>
        <p className="mt-2 text-sm text-fg-muted">
          Select a node to edit its configuration.
        </p>
      </aside>
    );
  }

  const { nodeType, label, config, isStart } = node.data;
  const setConfig = (patch: Record<string, unknown>) =>
    onChange({ config: { ...config, ...patch } });

  return (
    <aside aria-label="Node config" className="border-l hairline bg-bone p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <Eyebrow>{nodeType.replace("_", " ")}</Eyebrow>
          <p className="mt-1 font-mono text-[10px] text-fg-muted">id · {node.id}</p>
        </div>
        {isStart ? (
          <span className="rounded-sm border border-tan px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-eyebrow text-tan-text">
            start
          </span>
        ) : (
          <button
            type="button"
            onClick={onSetStart}
            disabled={readOnly}
            className="text-[10px] font-mono uppercase tracking-eyebrow text-tan-text hover:underline disabled:opacity-50"
          >
            Set as start
          </button>
        )}
      </div>

      <div className="mt-4 space-y-3">
        <Field label="Label" htmlFor={labelFieldId}>
          <input
            id={labelFieldId}
            type="text"
            value={label}
            disabled={readOnly}
            onChange={(e) => onChange({ label: e.target.value })}
            className={inputClass}
          />
        </Field>

        <NodeConfigForm
          nodeType={nodeType}
          config={config}
          readOnly={readOnly}
          onChange={setConfig}
        />
      </div>

      {!readOnly ? (
        <div className="mt-6 border-t hairline pt-3">
          <button
            type="button"
            onClick={onDelete}
            className="text-[11px] font-mono uppercase tracking-eyebrow text-[#8E3B30] hover:underline"
          >
            Delete node
          </button>
        </div>
      ) : null}
    </aside>
  );
};

const Field = ({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor?: string;
  children: React.ReactNode;
}) => (
  <label htmlFor={htmlFor} className="block">
    <span className="font-styrene text-[10px] font-bold uppercase tracking-eyebrow text-tan-text">
      {label}
    </span>
    <div className="mt-1">{children}</div>
  </label>
);

const inputClass =
  "block w-full rounded-sm border hairline bg-bone px-2.5 py-1.5 text-sm focus:border-tan focus:outline-none focus:ring-1 focus:ring-tan disabled:opacity-50";

const NodeConfigForm = ({
  nodeType,
  config,
  readOnly,
  onChange,
}: {
  nodeType: AutomationNodeType;
  config: Record<string, unknown>;
  readOnly: boolean;
  onChange: (patch: Record<string, unknown>) => void;
}) => {
  if (nodeType === "action") {
    return (
      <>
        <Field label="Action name">
          <input
            type="text"
            value={String(config.action ?? "")}
            disabled={readOnly}
            placeholder="e.g. crm.create_contact"
            onChange={(e) => onChange({ action: e.target.value })}
            className={inputClass}
          />
        </Field>
        <Field label="Input (JSON)">
          <JsonTextarea
            value={config.input}
            readOnly={readOnly}
            onChange={(input) => onChange({ input })}
          />
        </Field>
      </>
    );
  }

  if (nodeType === "delay") {
    return (
      <Field label="Seconds">
        <input
          type="number"
          min={0}
          value={Number(config.seconds ?? 0)}
          disabled={readOnly}
          onChange={(e) => onChange({ seconds: Number(e.target.value) || 0 })}
          className={inputClass}
        />
      </Field>
    );
  }

  if (nodeType === "approval") {
    return (
      <>
        <Field label="Summary">
          <textarea
            value={String(config.summary ?? "")}
            disabled={readOnly}
            rows={3}
            onChange={(e) => onChange({ summary: e.target.value })}
            className={inputClass}
          />
        </Field>
        <Field label="TTL (seconds)">
          <input
            type="number"
            min={60}
            value={Number(config.ttl_seconds ?? 604800)}
            disabled={readOnly}
            onChange={(e) => onChange({ ttl_seconds: Number(e.target.value) || 604800 })}
            className={inputClass}
          />
        </Field>
      </>
    );
  }

  if (nodeType === "branch") {
    return (
      <>
        <Field label="Field path">
          <input
            type="text"
            value={String(config.field ?? "")}
            placeholder="n1.score"
            disabled={readOnly}
            onChange={(e) => onChange({ field: e.target.value })}
            className={inputClass}
          />
        </Field>
        <Field label="Operator">
          <select
            value={String(config.op ?? "eq")}
            disabled={readOnly}
            onChange={(e) => onChange({ op: e.target.value })}
            className={inputClass}
          >
            <option value="eq">eq</option>
            <option value="neq">neq</option>
            <option value="gt">gt</option>
            <option value="gte">gte</option>
            <option value="lt">lt</option>
            <option value="lte">lte</option>
            <option value="in">in</option>
            <option value="is_null">is_null</option>
          </select>
        </Field>
        <Field label="Value (JSON)">
          <JsonTextarea
            value={config.value}
            readOnly={readOnly}
            onChange={(value) => onChange({ value })}
          />
        </Field>
      </>
    );
  }

  if (nodeType === "wait_for_event") {
    return (
      <Field label="Event key">
        <input
          type="text"
          value={String(config.event_key ?? "")}
          placeholder="gmail.reply_received"
          disabled={readOnly}
          onChange={(e) => onChange({ event_key: e.target.value })}
          className={inputClass}
        />
      </Field>
    );
  }

  // end nodes have no config.
  return (
    <p className="font-mono text-[11px] text-fg-muted">
      End nodes terminate the run.
    </p>
  );
};

const JsonTextarea = ({
  value,
  readOnly,
  onChange,
}: {
  value: unknown;
  readOnly: boolean;
  onChange: (parsed: unknown) => void;
}) => {
  const [draft, setDraft] = React.useState<string>(() => safeStringify(value));
  const [err, setErr] = React.useState<string | null>(null);
  // Re-seed from upstream when the selected node changes.
  const valueHash = React.useMemo(() => safeStringify(value), [value]);
  const lastValueHashRef = React.useRef(valueHash);
  React.useEffect(() => {
    if (valueHash !== lastValueHashRef.current) {
      lastValueHashRef.current = valueHash;
      setDraft(valueHash);
      setErr(null);
    }
  }, [valueHash]);

  return (
    <div>
      <textarea
        value={draft}
        rows={4}
        disabled={readOnly}
        onChange={(e) => {
          const next = e.target.value;
          setDraft(next);
          try {
            const parsed = next.trim() === "" ? null : JSON.parse(next);
            setErr(null);
            onChange(parsed);
          } catch (parseErr) {
            setErr(parseErr instanceof Error ? parseErr.message : String(parseErr));
          }
        }}
        className={inputClass + " font-mono text-[11px]"}
      />
      {err ? <p className="mt-1 text-[10px] text-[#8E3B30]">{err}</p> : null}
    </div>
  );
};

const safeStringify = (v: unknown) => {
  try {
    return v == null ? "" : JSON.stringify(v, null, 2);
  } catch {
    return "";
  }
};
