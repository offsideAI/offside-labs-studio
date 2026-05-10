"use client";

import * as React from "react";

import {
  type CustomFieldDef,
  type CustomFieldEntityType,
  useCustomFieldDefs,
} from "../lib/api";

interface Props {
  workspaceId: number;
  entityType: CustomFieldEntityType;
  values: Record<string, unknown>;
  onChange: (values: Record<string, unknown>) => void;
  disabled?: boolean;
}

export const CustomFieldsPanel = ({
  workspaceId,
  entityType,
  values,
  onChange,
  disabled,
}: Props) => {
  const defs = useCustomFieldDefs(workspaceId, entityType);

  if (defs.isLoading) {
    return <p className="text-sm text-fg-muted">Loading custom fields…</p>;
  }
  const list = defs.data?.results ?? [];
  if (list.length === 0) return null;

  const setValue = (key: string, value: unknown) => {
    onChange({ ...values, [key]: value });
  };

  return (
    <div className="space-y-4">
      {list.map((def) => (
        <CustomFieldInput
          key={def.id}
          def={def}
          value={values[def.key]}
          onChange={(v) => setValue(def.key, v)}
          disabled={disabled}
        />
      ))}
    </div>
  );
};

const CustomFieldInput = ({
  def,
  value,
  onChange,
  disabled,
}: {
  def: CustomFieldDef;
  value: unknown;
  onChange: (next: unknown) => void;
  disabled?: boolean;
}) => {
  const baseInput =
    "w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2";

  return (
    <div className="space-y-1.5">
      <label htmlFor={`cf-${def.key}`} className="text-sm font-medium">
        {def.label}
        {def.required ? <span className="text-tan-text"> *</span> : null}
      </label>
      {(() => {
        switch (def.type) {
          case "long_text":
            return (
              <textarea
                id={`cf-${def.key}`}
                value={(value as string) ?? ""}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled}
                rows={3}
                className={baseInput}
              />
            );
          case "number":
            return (
              <input
                id={`cf-${def.key}`}
                type="number"
                value={(value as number | undefined) ?? ""}
                onChange={(e) =>
                  onChange(e.target.value === "" ? null : Number(e.target.value))
                }
                disabled={disabled}
                className={baseInput}
              />
            );
          case "boolean":
            return (
              <input
                id={`cf-${def.key}`}
                type="checkbox"
                checked={Boolean(value)}
                onChange={(e) => onChange(e.target.checked)}
                disabled={disabled}
              />
            );
          case "date":
            return (
              <input
                id={`cf-${def.key}`}
                type="date"
                value={(value as string) ?? ""}
                onChange={(e) => onChange(e.target.value || null)}
                disabled={disabled}
                className={baseInput}
              />
            );
          case "datetime":
            return (
              <input
                id={`cf-${def.key}`}
                type="datetime-local"
                value={(value as string) ?? ""}
                onChange={(e) => onChange(e.target.value || null)}
                disabled={disabled}
                className={baseInput}
              />
            );
          case "select":
            return (
              <select
                id={`cf-${def.key}`}
                value={(value as string) ?? ""}
                onChange={(e) => onChange(e.target.value || null)}
                disabled={disabled}
                className={baseInput}
              >
                <option value="">—</option>
                {def.options.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            );
          default:
            // text, url, email, phone, multi_select (basic), relation (basic)
            return (
              <input
                id={`cf-${def.key}`}
                type={def.type === "email" ? "email" : def.type === "url" ? "url" : "text"}
                value={(value as string) ?? ""}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled}
                className={baseInput}
              />
            );
        }
      })()}
    </div>
  );
};
