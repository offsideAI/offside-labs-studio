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

export { AuthFetchError };
