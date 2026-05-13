// Single source of truth for the web app's API surface. Built on
// @offside/auth-utils — handles Bearer auth, refresh-on-401, and the
// X-Workspace-Id header. Hooks return TanStack Query results so callers
// don't manage loading/error state by hand.

"use client";

import {
  AuthFetchError,
  browserTokenStore,
  createAuthFetch,
  type Tokens,
} from "@offside/auth-utils";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const tokenStore = browserTokenStore();

let onAuthFailure: (() => void) | undefined;
export const setAuthFailureHandler = (handler: () => void) => {
  onAuthFailure = handler;
};

const fetcher = createAuthFetch({
  baseUrl,
  store: tokenStore,
  refreshPath: "/api/auth/token/refresh/",
  onAuthFailure: () => onAuthFailure?.(),
});

export const apiTokens = {
  set: (tokens: Tokens) => tokenStore.set(tokens),
  clear: () => tokenStore.clear(),
  hasSession: () => Boolean(tokenStore.get()?.access),
};

// --- Domain types (loose; replaced by OpenAPI codegen output once `pnpm codegen:openapi` runs) ---

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url: string;
  date_joined: string;
}

export interface Workspace {
  id: number;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
  updated_at: string;
  role: string | null;
}

export interface Membership {
  id: number;
  user: number;
  user_email: string;
  user_full_name: string;
  workspace: number;
  role: string;
  joined_at: string;
  deactivated_at: string | null;
}

export interface Invitation {
  id: number;
  email: string;
  role: string;
  workspace: number;
  workspace_name: string;
  invited_by: number;
  invited_by_email: string;
  created_at: string;
  expires_at: string;
  accepted_at: string | null;
}

export interface PublicInvitationDetail {
  email: string;
  role: string;
  workspace_name: string;
  workspace_slug: string;
  invited_by_email: string;
  is_expired: boolean;
  is_accepted: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

// --- Auth ---

export const useCurrentUser = () =>
  useQuery({
    queryKey: ["currentUser"],
    queryFn: () => fetcher.authFetch<User>("/api/auth/user/"),
    enabled: apiTokens.hasSession(),
    retry: false,
  });

export const useLogin = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { email: string; password: string }) => {
      const data = await fetcher.authFetch<LoginResponse>("/api/auth/login/", {
        method: "POST",
        body: input,
      });
      apiTokens.set({ access: data.access, refresh: data.refresh });
      return data;
    },
    onSuccess: (data) => {
      qc.setQueryData(["currentUser"], data.user);
      qc.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
};

export const useSignup = () =>
  useMutation({
    mutationFn: (input: {
      email: string;
      password1: string;
      password2: string;
      full_name?: string;
    }) =>
      fetcher.authFetch<unknown>("/api/auth/registration/", {
        method: "POST",
        body: input,
      }),
  });

export const useLogout = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      try {
        await fetcher.authFetch("/api/auth/logout/", { method: "POST" });
      } finally {
        apiTokens.clear();
      }
    },
    onSuccess: () => qc.clear(),
  });
};

// --- Workspaces ---

export const useWorkspaces = () =>
  useQuery({
    queryKey: ["workspaces"],
    queryFn: () => fetcher.authFetch<Paginated<Workspace>>("/api/workspaces/"),
    enabled: apiTokens.hasSession(),
  });

export const useCreateWorkspace = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string }) =>
      fetcher.authFetch<Workspace>("/api/workspaces/", {
        method: "POST",
        body: input,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
};

export const useArchiveWorkspace = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      fetcher.authFetch<{ id: number; deleted_at: string }>(
        `/api/workspaces/${workspaceId}/archive/`,
        { method: "POST", workspaceId: workspaceId ?? undefined },
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workspaces"] }),
  });
};

// --- Memberships (workspace-scoped — requires X-Workspace-Id) ---

export const useMemberships = (workspaceId: number | null | undefined) =>
  useQuery({
    queryKey: ["memberships", workspaceId],
    queryFn: () =>
      fetcher.authFetch<Paginated<Membership>>("/api/memberships/", {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useUpdateMembershipRole = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { membershipId: number; role: string }) =>
      fetcher.authFetch<Membership>(`/api/memberships/${input.membershipId}/`, {
        method: "PATCH",
        body: { role: input.role },
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memberships", workspaceId] }),
  });
};

// --- Invitations (workspace-scoped) ---

export const useInvitations = (workspaceId: number | null | undefined) =>
  useQuery({
    queryKey: ["invitations", workspaceId],
    queryFn: () =>
      fetcher.authFetch<Paginated<Invitation>>("/api/invitations/", {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useCreateInvitation = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { email: string; role: string }) =>
      fetcher.authFetch<Invitation>("/api/invitations/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["invitations", workspaceId] }),
  });
};

// --- Invitation acceptance ---

export const usePublicInvitation = (token: string) =>
  useQuery({
    queryKey: ["public-invitation", token],
    queryFn: () => fetcher.authFetch<PublicInvitationDetail>(`/api/invitations/${token}/`),
    enabled: Boolean(token),
  });

export const useAcceptInvitation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (token: string) =>
      fetcher.authFetch<{
        workspace_id: number;
        workspace_slug: string;
        role: string;
        created: boolean;
      }>(`/api/invitations/${token}/accept/`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workspaces"] }),
  });
};

// --- M4: Contacts, Companies, Custom field defs ---

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  primary_email: string;
  phones: Array<{ label?: string; number: string }>;
  title: string;
  company: number | null;
  owner: number | null;
  lifecycle_stage: string;
  source: string;
  custom: Record<string, unknown>;
  tags: string[];
  created_by: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface Company {
  id: number;
  name: string;
  domain: string;
  size_band: string;
  industry: string;
  owner: number | null;
  custom: Record<string, unknown>;
  tags: string[];
  created_by: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export type CustomFieldType =
  | "text"
  | "long_text"
  | "number"
  | "select"
  | "multi_select"
  | "date"
  | "datetime"
  | "boolean"
  | "url"
  | "email"
  | "phone"
  | "relation";

export type CustomFieldEntityType = "contact" | "company" | "deal" | "task" | "note";

export interface CustomFieldDef {
  id: number;
  entity_type: CustomFieldEntityType;
  key: string;
  label: string;
  type: CustomFieldType;
  options: string[];
  required: boolean;
  indexed: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

const buildContactsUrl = (filter?: Record<string, unknown>) => {
  if (!filter) return "/api/contacts/";
  return `/api/contacts/?filter=${encodeURIComponent(JSON.stringify(filter))}`;
};

const buildCompaniesUrl = (filter?: Record<string, unknown>) => {
  if (!filter) return "/api/companies/";
  return `/api/companies/?filter=${encodeURIComponent(JSON.stringify(filter))}`;
};

// --- Contacts ---

export const useContacts = (
  workspaceId: number | null | undefined,
  filter?: Record<string, unknown>,
) =>
  useQuery({
    queryKey: ["contacts", workspaceId, filter],
    queryFn: () =>
      fetcher.authFetch<Paginated<Contact>>(buildContactsUrl(filter), {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useContact = (workspaceId: number | null | undefined, contactId: number | string) =>
  useQuery({
    queryKey: ["contact", workspaceId, String(contactId)],
    queryFn: () =>
      fetcher.authFetch<Contact>(`/api/contacts/${contactId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && contactId) && apiTokens.hasSession(),
  });

export const useCreateContact = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Contact>) =>
      fetcher.authFetch<Contact>("/api/contacts/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["contacts", workspaceId] }),
  });
};

export const useUpdateContact = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number | string; patch: Partial<Contact> }) =>
      fetcher.authFetch<Contact>(`/api/contacts/${input.id}/`, {
        method: "PATCH",
        body: input.patch,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ["contacts", workspaceId] });
      qc.invalidateQueries({ queryKey: ["contact", workspaceId, String(vars.id)] });
    },
  });
};

export const useDeleteContact = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      fetcher.authFetch<unknown>(`/api/contacts/${id}/`, {
        method: "DELETE",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["contacts", workspaceId] }),
  });
};

// --- Companies ---

export const useCompanies = (
  workspaceId: number | null | undefined,
  filter?: Record<string, unknown>,
) =>
  useQuery({
    queryKey: ["companies", workspaceId, filter],
    queryFn: () =>
      fetcher.authFetch<Paginated<Company>>(buildCompaniesUrl(filter), {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useCompany = (workspaceId: number | null | undefined, companyId: number | string) =>
  useQuery({
    queryKey: ["company", workspaceId, String(companyId)],
    queryFn: () =>
      fetcher.authFetch<Company>(`/api/companies/${companyId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && companyId) && apiTokens.hasSession(),
  });

export const useCreateCompany = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Company>) =>
      fetcher.authFetch<Company>("/api/companies/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies", workspaceId] }),
  });
};

export const useUpdateCompany = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number | string; patch: Partial<Company> }) =>
      fetcher.authFetch<Company>(`/api/companies/${input.id}/`, {
        method: "PATCH",
        body: input.patch,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ["companies", workspaceId] });
      qc.invalidateQueries({ queryKey: ["company", workspaceId, String(vars.id)] });
    },
  });
};

export const useDeleteCompany = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      fetcher.authFetch<unknown>(`/api/companies/${id}/`, {
        method: "DELETE",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies", workspaceId] }),
  });
};

// --- Custom field defs ---

export const useCustomFieldDefs = (
  workspaceId: number | null | undefined,
  entityType?: CustomFieldEntityType,
) =>
  useQuery({
    queryKey: ["custom-field-defs", workspaceId, entityType],
    queryFn: () =>
      fetcher.authFetch<Paginated<CustomFieldDef>>(
        entityType
          ? `/api/custom-field-defs/?entity_type=${entityType}`
          : "/api/custom-field-defs/",
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useCreateCustomFieldDef = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<CustomFieldDef>) =>
      fetcher.authFetch<CustomFieldDef>("/api/custom-field-defs/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["custom-field-defs", workspaceId] }),
  });
};

export const useDeleteCustomFieldDef = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      fetcher.authFetch<unknown>(`/api/custom-field-defs/${id}/`, {
        method: "DELETE",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["custom-field-defs", workspaceId] }),
  });
};

// --- CSV imports ---

export type ImportEntityType = "contact" | "company";
export type ImportStatus = "pending" | "running" | "complete" | "failed";

export interface ImportRun {
  id: number;
  entity_type: ImportEntityType;
  file_name: string;
  mapping: Record<string, string>;
  status: ImportStatus;
  total_rows: number;
  processed_rows: number;
  error_rows: number;
  errors: Array<{ row: number | null; message: string }>;
  headers: string[];
  sample_rows: string[][];
  progress_pct: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export const useUploadImportCSV = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { file: File; entityType: ImportEntityType }) => {
      const fd = new FormData();
      fd.append("entity_type", input.entityType);
      fd.append("file", input.file);
      return fetcher.authFetch<ImportRun>("/api/imports/upload/", {
        method: "POST",
        body: fd,
        workspaceId: workspaceId ?? undefined,
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["imports", workspaceId] }),
  });
};

export const useUpdateImportMapping = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number; mapping: Record<string, string> }) =>
      fetcher.authFetch<ImportRun>(`/api/imports/${input.id}/`, {
        method: "PATCH",
        body: { mapping: input.mapping },
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (run) => qc.setQueryData<ImportRun>(["import-run", workspaceId, run.id], run),
  });
};

export const useCommitImport = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetcher.authFetch<ImportRun>(`/api/imports/${id}/commit/`, {
        method: "POST",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (run) => qc.setQueryData<ImportRun>(["import-run", workspaceId, run.id], run),
  });
};

export const useImportRun = (
  workspaceId: number | null | undefined,
  importId: number | null | undefined,
  poll = false,
) =>
  useQuery({
    queryKey: ["import-run", workspaceId, importId],
    queryFn: () =>
      fetcher.authFetch<ImportRun>(`/api/imports/${importId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && importId) && apiTokens.hasSession(),
    refetchInterval: poll ? 1500 : false,
  });

// --- M5: Pipelines, Deals, Tasks, Notes, Activities ---

export interface PipelineStage {
  id: string;
  label: string;
  order: number;
}

export interface Pipeline {
  id: number;
  name: string;
  stages: PipelineStage[];
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface Deal {
  id: number;
  name: string;
  pipeline: number;
  stage_id: string;
  value_cents: number;
  currency: string;
  expected_close: string | null;
  contact: number | null;
  company: number | null;
  owner: number | null;
  custom: Record<string, unknown>;
  tags: string[];
  created_by: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export type RelatedType = "contact" | "company" | "deal" | "task" | "note";
export type TaskStatus = "open" | "in_progress" | "done" | "cancelled";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: number;
  title: string;
  description: string;
  due_at: string | null;
  related_type: RelatedType;
  related_id: number;
  status: TaskStatus;
  priority: TaskPriority;
  owner: number | null;
  custom: Record<string, unknown>;
  completed_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface Note {
  id: number;
  body_md: string;
  related_type: RelatedType;
  related_id: number;
  author: number;
  edit_log: Array<{ edited_at: string; edited_by: number; previous_body_preview: string }>;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export type ActivityKind =
  | "record_created"
  | "record_updated"
  | "field_changed"
  | "note_added"
  | "task_created"
  | "task_completed"
  | "deal_stage_changed"
  | "email_sent"
  | "email_received"
  | "ai_action"
  | "automation_run";

export interface Activity {
  id: number;
  kind: ActivityKind;
  actor_kind: string;
  actor_user: number | null;
  actor_email: string | null;
  related_type: RelatedType;
  related_id: number;
  payload: Record<string, unknown>;
  occurred_at: string;
}

// --- Pipelines ---

export const usePipelines = (workspaceId: number | null | undefined) =>
  useQuery({
    queryKey: ["pipelines", workspaceId],
    queryFn: () =>
      fetcher.authFetch<Paginated<Pipeline>>("/api/pipelines/", {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useCreatePipeline = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string; stages?: PipelineStage[] }) =>
      fetcher.authFetch<Pipeline>("/api/pipelines/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pipelines", workspaceId] }),
  });
};

// --- Deals ---

export const useDeals = (
  workspaceId: number | null | undefined,
  filter?: Record<string, unknown>,
) =>
  useQuery({
    queryKey: ["deals", workspaceId, filter],
    queryFn: () => {
      const url = filter
        ? `/api/deals/?filter=${encodeURIComponent(JSON.stringify(filter))}`
        : "/api/deals/";
      return fetcher.authFetch<Paginated<Deal>>(url, {
        workspaceId: workspaceId ?? undefined,
      });
    },
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useDeal = (workspaceId: number | null | undefined, dealId: number | string) =>
  useQuery({
    queryKey: ["deal", workspaceId, String(dealId)],
    queryFn: () =>
      fetcher.authFetch<Deal>(`/api/deals/${dealId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && dealId) && apiTokens.hasSession(),
  });

export const useCreateDeal = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Deal>) =>
      fetcher.authFetch<Deal>("/api/deals/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["deals", workspaceId] }),
  });
};

export const useUpdateDeal = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number | string; patch: Partial<Deal> }) =>
      fetcher.authFetch<Deal>(`/api/deals/${input.id}/`, {
        method: "PATCH",
        body: input.patch,
        workspaceId: workspaceId ?? undefined,
      }),
    // Optimistic update for kanban drag-drop responsiveness.
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: ["deals", workspaceId] });
      const previous = qc.getQueriesData<Paginated<Deal>>({ queryKey: ["deals", workspaceId] });
      qc.setQueriesData<Paginated<Deal>>(
        { queryKey: ["deals", workspaceId] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            results: old.results.map((d) =>
              d.id === Number(input.id) ? { ...d, ...input.patch } : d,
            ),
          };
        },
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      context?.previous.forEach(([key, value]) => qc.setQueryData(key, value));
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["deals", workspaceId] }),
  });
};

export const useDeleteDeal = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      fetcher.authFetch<unknown>(`/api/deals/${id}/`, {
        method: "DELETE",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["deals", workspaceId] }),
  });
};

// --- Tasks ---

export const useTasksFor = (
  workspaceId: number | null | undefined,
  relatedType: RelatedType | null | undefined,
  relatedId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["tasks", workspaceId, relatedType, String(relatedId)],
    queryFn: () =>
      fetcher.authFetch<Paginated<Task>>(
        `/api/tasks/?related_type=${relatedType}&related_id=${relatedId}`,
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled:
      Boolean(workspaceId && relatedType && relatedId) && apiTokens.hasSession(),
  });

export const useCreateTask = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Task>) =>
      fetcher.authFetch<Task>("/api/tasks/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (task) =>
      qc.invalidateQueries({
        queryKey: ["tasks", workspaceId, task.related_type, String(task.related_id)],
      }),
  });
};

export const useUpdateTask = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number; patch: Partial<Task> }) =>
      fetcher.authFetch<Task>(`/api/tasks/${input.id}/`, {
        method: "PATCH",
        body: input.patch,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (task) =>
      qc.invalidateQueries({
        queryKey: ["tasks", workspaceId, task.related_type, String(task.related_id)],
      }),
  });
};

// --- Notes ---

export const useNotesFor = (
  workspaceId: number | null | undefined,
  relatedType: RelatedType | null | undefined,
  relatedId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["notes", workspaceId, relatedType, String(relatedId)],
    queryFn: () =>
      fetcher.authFetch<Paginated<Note>>(
        `/api/notes/?related_type=${relatedType}&related_id=${relatedId}`,
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled:
      Boolean(workspaceId && relatedType && relatedId) && apiTokens.hasSession(),
  });

export const useCreateNote = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { body_md: string; related_type: RelatedType; related_id: number }) =>
      fetcher.authFetch<Note>("/api/notes/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (note) =>
      qc.invalidateQueries({
        queryKey: ["notes", workspaceId, note.related_type, String(note.related_id)],
      }),
  });
};

// --- Activities ---

export const useActivitiesFor = (
  workspaceId: number | null | undefined,
  relatedType: RelatedType | null | undefined,
  relatedId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["activities", workspaceId, relatedType, String(relatedId)],
    queryFn: () =>
      fetcher.authFetch<Paginated<Activity>>(
        `/api/activities/?related_type=${relatedType}&related_id=${relatedId}`,
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled:
      Boolean(workspaceId && relatedType && relatedId) && apiTokens.hasSession(),
  });

// --- M8: Automations (workflow editor + run inspector) ---

export type AutomationStatus = "draft" | "active" | "paused" | "archived";

export type AutomationNodeType =
  | "action"
  | "delay"
  | "approval"
  | "branch"
  | "wait_for_event"
  | "end";

export interface AutomationNode {
  type: AutomationNodeType;
  config?: Record<string, unknown>;
  next?: string;
  approve_next?: string;
  reject_next?: string;
  true_next?: string;
  false_next?: string;
  // Editor-only positioning (the backend ignores extra keys).
  position?: { x: number; y: number };
  label?: string;
}

export interface AutomationGraph {
  start_node_id?: string;
  nodes?: Record<string, AutomationNode>;
}

export interface Automation {
  id: number;
  name: string;
  description: string;
  status: AutomationStatus;
  trigger: Record<string, unknown>;
  graph: AutomationGraph;
  version: number;
  published_version: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface AutomationVersion {
  id: number;
  automation: number;
  version_number: number;
  graph: AutomationGraph;
  trigger: Record<string, unknown>;
  published_by: number;
  published_at: string;
}

export type RunStatus =
  | "pending"
  | "running"
  | "awaiting_approval"
  | "awaiting_delay"
  | "awaiting_event"
  | "completed"
  | "failed"
  | "cancelled";

export interface AutomationStepRun {
  id: number;
  step_id: string;
  attempt: number;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string | null;
  finished_at: string | null;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  model: string;
  cost_cents: number;
  error: { type?: string; message?: string } | null;
  idempotency_key: string;
}

export interface AutomationRun {
  id: number;
  automation: number;
  version: number | null;
  status: RunStatus;
  current_step_id: string;
  trigger_payload: Record<string, unknown>;
  resume_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  attempt: number;
  state_snapshot?: Record<string, Record<string, unknown>>;
  step_runs?: AutomationStepRun[];
}

export const useAutomations = (workspaceId: number | null | undefined) =>
  useQuery({
    queryKey: ["automations", workspaceId],
    queryFn: () =>
      fetcher.authFetch<Paginated<Automation>>("/api/automations/", {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId) && apiTokens.hasSession(),
  });

export const useAutomation = (
  workspaceId: number | null | undefined,
  automationId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["automation", workspaceId, String(automationId)],
    queryFn: () =>
      fetcher.authFetch<Automation>(`/api/automations/${automationId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && automationId) && apiTokens.hasSession(),
  });

export const useCreateAutomation = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Pick<Automation, "name" | "description" | "graph" | "trigger">>) =>
      fetcher.authFetch<Automation>("/api/automations/", {
        method: "POST",
        body: input,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["automations", workspaceId] }),
  });
};

export const useUpdateAutomation = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number | string; patch: Partial<Automation> }) =>
      fetcher.authFetch<Automation>(`/api/automations/${input.id}/`, {
        method: "PATCH",
        body: input.patch,
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (auto) => {
      qc.setQueryData<Automation>(["automation", workspaceId, String(auto.id)], auto);
      qc.invalidateQueries({ queryKey: ["automations", workspaceId] });
    },
  });
};

export const usePublishAutomation = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      fetcher.authFetch<AutomationVersion>(`/api/automations/${id}/publish/`, {
        method: "POST",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (_v, id) => {
      qc.invalidateQueries({ queryKey: ["automation", workspaceId, String(id)] });
      qc.invalidateQueries({ queryKey: ["automation-versions", workspaceId, String(id)] });
      qc.invalidateQueries({ queryKey: ["automations", workspaceId] });
    },
  });
};

export const useAutomationVersions = (
  workspaceId: number | null | undefined,
  automationId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["automation-versions", workspaceId, String(automationId)],
    queryFn: () =>
      fetcher.authFetch<Paginated<AutomationVersion>>(
        `/api/automations/${automationId}/versions/`,
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled: Boolean(workspaceId && automationId) && apiTokens.hasSession(),
  });

export const useStartAutomationRun = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: number | string; trigger_payload?: Record<string, unknown> }) =>
      fetcher.authFetch<AutomationRun>(`/api/automations/${input.id}/start_run/`, {
        method: "POST",
        body: { trigger_payload: input.trigger_payload ?? {} },
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (_run, vars) =>
      qc.invalidateQueries({
        queryKey: ["automation-runs", workspaceId, String(vars.id)],
      }),
  });
};

export const useAutomationRuns = (
  workspaceId: number | null | undefined,
  automationId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["automation-runs", workspaceId, String(automationId)],
    queryFn: () =>
      fetcher.authFetch<Paginated<AutomationRun>>(
        `/api/automation-runs/?automation=${automationId}`,
        { workspaceId: workspaceId ?? undefined },
      ),
    enabled: Boolean(workspaceId && automationId) && apiTokens.hasSession(),
  });

export const useAutomationRun = (
  workspaceId: number | null | undefined,
  runId: number | string | null | undefined,
) =>
  useQuery({
    queryKey: ["automation-run", workspaceId, String(runId)],
    queryFn: () =>
      fetcher.authFetch<AutomationRun>(`/api/automation-runs/${runId}/`, {
        workspaceId: workspaceId ?? undefined,
      }),
    enabled: Boolean(workspaceId && runId) && apiTokens.hasSession(),
  });

export interface GenerateFromNLResponse {
  graph: AutomationGraph;
  model: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
}

export const useGenerateFromNL = (workspaceId: number | null | undefined) =>
  useMutation({
    mutationFn: (input: {
      id: number | string;
      description: string;
      workspace_context?: string;
    }) =>
      fetcher.authFetch<GenerateFromNLResponse>(
        `/api/automations/${input.id}/generate_from_nl/`,
        {
          method: "POST",
          body: {
            description: input.description,
            workspace_context: input.workspace_context ?? "",
          },
          workspaceId: workspaceId ?? undefined,
        },
      ),
  });

export const useCancelAutomationRun = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (runId: number | string) =>
      fetcher.authFetch<AutomationRun>(`/api/automation-runs/${runId}/cancel/`, {
        method: "POST",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: (run) => {
      qc.setQueryData(["automation-run", workspaceId, String(run.id)], run);
      qc.invalidateQueries({
        queryKey: ["automation-runs", workspaceId, String(run.automation)],
      });
    },
  });
};

// --- M9.S4: Agents Marketplace ---

export type MarketplaceAgentCategory =
  | "lead_management"
  | "deal_hygiene"
  | "comms"
  | "integrations"
  | "operations"
  | "cart_recovery"
  | "fulfillment"
  | "payments"
  | "customer_service";

export interface MarketplaceAgentSummary {
  id: number;
  slug: string;
  name: string;
  description: string;
  category: MarketplaceAgentCategory;
  icon_emoji: string;
  author: string;
  install_count: number;
  published_at: string;
}

export interface MarketplaceAgentDetail extends MarketplaceAgentSummary {
  long_description: string;
  graph: AutomationGraph;
  trigger: Record<string, unknown>;
  updated_at: string;
}

export interface InstallResponse {
  automation_id: number;
  automation_name: string;
  version_number: number;
  install_id: number;
}

// Marketplace catalog list + detail are anon-readable, so we don't pass a
// workspaceId / Authorization header on those requests.
export const useMarketplaceAgents = (category?: MarketplaceAgentCategory) =>
  useQuery({
    queryKey: ["marketplace-agents", category ?? null],
    queryFn: () =>
      fetcher.authFetch<Paginated<MarketplaceAgentSummary>>(
        category
          ? `/api/marketplace/agents/?category=${category}`
          : "/api/marketplace/agents/",
      ),
  });

export const useMarketplaceAgent = (slug: string | null | undefined) =>
  useQuery({
    queryKey: ["marketplace-agent", slug],
    queryFn: () =>
      fetcher.authFetch<MarketplaceAgentDetail>(`/api/marketplace/agents/${slug}/`),
    enabled: Boolean(slug),
  });

export const useInstallMarketplaceAgent = (workspaceId: number | null | undefined) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (slug: string) =>
      fetcher.authFetch<InstallResponse>(`/api/marketplace/agents/${slug}/install/`, {
        method: "POST",
        workspaceId: workspaceId ?? undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["automations", workspaceId] });
      qc.invalidateQueries({ queryKey: ["marketplace-agents"] });
    },
  });
};

export { AuthFetchError };
