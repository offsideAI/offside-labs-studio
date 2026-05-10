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

export { AuthFetchError };
