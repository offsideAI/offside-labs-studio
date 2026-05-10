"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import * as React from "react";

import {
  type CustomFieldDef,
  type CustomFieldEntityType,
  type CustomFieldType,
  useCreateCustomFieldDef,
  useCustomFieldDefs,
  useDeleteCustomFieldDef,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";

const ENTITY_TYPES: Array<{ value: CustomFieldEntityType; label: string }> = [
  { value: "contact", label: "Contact" },
  { value: "company", label: "Company" },
];

const FIELD_TYPES: Array<{ value: CustomFieldType; label: string }> = [
  { value: "text", label: "Text" },
  { value: "long_text", label: "Long text" },
  { value: "number", label: "Number" },
  { value: "select", label: "Select" },
  { value: "multi_select", label: "Multi-select" },
  { value: "date", label: "Date" },
  { value: "datetime", label: "Datetime" },
  { value: "boolean", label: "Boolean" },
  { value: "url", label: "URL" },
  { value: "email", label: "Email" },
  { value: "phone", label: "Phone" },
  { value: "relation", label: "Relation" },
];

export default function CustomFieldsSettingsPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  const isAdmin = active.role === "owner" || active.role === "admin";
  return <CustomFieldsSettings workspaceId={active.id} workspaceSlug={active.slug} canEdit={isAdmin} />;
}

const CustomFieldsSettings = ({
  workspaceId,
  workspaceSlug,
  canEdit,
}: {
  workspaceId: number;
  workspaceSlug: string;
  canEdit: boolean;
}) => {
  const [entity, setEntity] = React.useState<CustomFieldEntityType>("contact");
  const defs = useCustomFieldDefs(workspaceId, entity);
  const create = useCreateCustomFieldDef(workspaceId);
  const remove = useDeleteCustomFieldDef(workspaceId);

  return (
    <div className="container-editorial section-rhythm space-y-10 py-12">
      <div>
        <Link href={`/${workspaceSlug}/settings`} className="link-tan text-sm">
          ← Settings
        </Link>
      </div>
      <header>
        <Eyebrow>Settings · Custom fields</Eyebrow>
        <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
          Define your fields<span className="tan-period">.</span>
        </h1>
        <p className="mt-3 text-fg-muted">
          Custom fields are workspace-scoped and per-entity. Values live in each record&rsquo;s
          JSONB column; defs here describe the schema (label, type, options).
        </p>
      </header>

      <Hairline />

      <div className="flex gap-2">
        {ENTITY_TYPES.map((et) => (
          <button
            key={et.value}
            type="button"
            onClick={() => setEntity(et.value)}
            className={
              "rounded-sm border px-3 py-1.5 text-sm transition-colors " +
              (entity === et.value
                ? "border-ink bg-ink text-bone"
                : "hairline bg-bone text-ink hover:bg-tan-100")
            }
          >
            {et.label}
          </button>
        ))}
      </div>

      <ul className="divide-y hairline rounded-md border hairline bg-bone">
        {defs.isLoading ? (
          <li className="px-4 py-3 text-fg-muted">Loading…</li>
        ) : (defs.data?.results ?? []).length === 0 ? (
          <li className="px-4 py-3 text-fg-muted">No custom fields for {entity} yet.</li>
        ) : (
          (defs.data?.results ?? []).map((def: CustomFieldDef) => (
            <li key={def.id} className="flex items-center justify-between gap-4 px-4 py-3">
              <div className="space-y-1">
                <p className="font-medium">{def.label}</p>
                <p className="font-mono text-xs text-fg-muted">
                  {def.entity_type}.{def.key} · {def.type}
                  {def.required ? " · required" : ""}
                </p>
              </div>
              <div className="flex items-center gap-3">
                {def.type === "select" || def.type === "multi_select" ? (
                  <span className="font-mono text-xs text-fg-muted">
                    options: [{def.options.join(", ")}]
                  </span>
                ) : null}
                {canEdit ? (
                  <button
                    type="button"
                    onClick={async () => {
                      if (!window.confirm(`Delete custom field ${def.key}?`)) return;
                      await remove.mutateAsync(def.id);
                    }}
                    className="text-xs text-[#8E3B30] hover:underline"
                  >
                    delete
                  </button>
                ) : null}
              </div>
            </li>
          ))
        )}
      </ul>

      {canEdit ? <NewFieldForm workspaceId={workspaceId} entity={entity} create={create} /> : null}
    </div>
  );
};

const NewFieldForm = ({
  workspaceId: _workspaceId,
  entity,
  create,
}: {
  workspaceId: number;
  entity: CustomFieldEntityType;
  create: ReturnType<typeof useCreateCustomFieldDef>;
}) => {
  const [key, setKey] = React.useState("");
  const [label, setLabel] = React.useState("");
  const [type, setType] = React.useState<CustomFieldType>("text");
  const [options, setOptions] = React.useState("");
  const [required, setRequired] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await create.mutateAsync({
        entity_type: entity,
        key,
        label,
        type,
        options:
          type === "select" || type === "multi_select"
            ? options
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean)
            : [],
        required,
      });
      setKey("");
      setLabel("");
      setOptions("");
      setRequired(false);
    } catch {
      setError("Could not create custom field. Key may already exist.");
    }
  };

  return (
    <Card>
      <CardHeader>
        <Eyebrow>Add a field</Eyebrow>
        <h3 className="text-xl font-styrene font-bold">New {entity} field.</h3>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-3">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <Field label="Key (unique, slug)" htmlFor="cf-key">
              <input
                id="cf-key"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="lead_score"
                required
                pattern="[a-z0-9_-]+"
                className="input"
              />
            </Field>
            <Field label="Label" htmlFor="cf-label">
              <input
                id="cf-label"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Lead score"
                required
                className="input"
              />
            </Field>
          </div>
          <Field label="Type" htmlFor="cf-type">
            <select
              id="cf-type"
              value={type}
              onChange={(e) => setType(e.target.value as CustomFieldType)}
              className="input"
            >
              {FIELD_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </Field>
          {type === "select" || type === "multi_select" ? (
            <Field label="Options (comma-separated)" htmlFor="cf-options">
              <input
                id="cf-options"
                value={options}
                onChange={(e) => setOptions(e.target.value)}
                placeholder="A, B, C"
                className="input"
              />
            </Field>
          ) : null}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={required}
              onChange={(e) => setRequired(e.target.checked)}
            />
            Required
          </label>
          {error ? (
            <p role="alert" className="text-sm text-[#8E3B30]">
              {error}
            </p>
          ) : null}
          <button type="submit" disabled={create.isPending} className="button-primary">
            {create.isPending ? "Creating…" : "Create field"}
          </button>
        </form>

        <style jsx>{`
          .input {
            width: 100%;
            padding: 0.5rem 0.75rem;
            background: var(--brand-bone);
            border: 1px solid var(--brand-rule);
            border-radius: 4px;
            color: var(--brand-ink);
            font-size: 0.9rem;
          }
          .input:focus-visible {
            outline: 2px solid var(--brand-tan);
            outline-offset: 2px;
          }
          .button-primary {
            background: var(--brand-ink);
            color: var(--brand-bone);
            border: 1px solid var(--brand-ink);
            border-radius: 4px;
            padding: 0.5rem 1.25rem;
            font-weight: 700;
            font-size: 0.875rem;
            cursor: pointer;
          }
          .button-primary:hover { background: #303030; }
          .button-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        `}</style>
      </CardContent>
    </Card>
  );
};

const Field = ({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) => (
  <div className="space-y-1.5">
    <label htmlFor={htmlFor} className="text-sm font-medium">
      {label}
    </label>
    {children}
  </div>
);
