// Fetch wrapper that:
//   - Attaches the Bearer access token from the configured TokenStore.
//   - Attaches the X-Workspace-Id header when a workspaceId is provided.
//   - Refreshes the access token once on 401 and replays the request.
//   - Calls onAuthFailure if refresh fails so the app can redirect to /login.
//
// Returns the parsed JSON body on 2xx; throws AuthFetchError on non-2xx.

import { AuthFetchError, type AuthFetchConfig, type AuthFetchOptions } from "./types";

export const createAuthFetch = (config: AuthFetchConfig) => {
  const refreshPath = config.refreshPath ?? "/api/auth/token/refresh/";

  const performRequest = async (path: string, opts: AuthFetchOptions): Promise<Response> => {
    const headers = new Headers(opts.headers);
    if (!headers.has("Content-Type") && opts.body !== undefined) {
      headers.set("Content-Type", "application/json");
    }
    const tokens = config.store.get();
    if (tokens?.access) {
      headers.set("Authorization", `Bearer ${tokens.access}`);
    }
    if (opts.workspaceId !== undefined && opts.workspaceId !== null) {
      headers.set("X-Workspace-Id", String(opts.workspaceId));
    }
    const init: RequestInit = {
      ...opts,
      headers,
      body:
        opts.body === undefined
          ? undefined
          : typeof opts.body === "string"
            ? opts.body
            : JSON.stringify(opts.body),
    };
    return fetch(`${config.baseUrl}${path}`, init);
  };

  const refreshTokens = async (): Promise<boolean> => {
    const tokens = config.store.get();
    if (!tokens?.refresh) return false;
    const resp = await fetch(`${config.baseUrl}${refreshPath}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh }),
    });
    if (!resp.ok) {
      config.store.clear();
      config.onAuthFailure?.();
      return false;
    }
    const data = (await resp.json()) as { access: string; refresh?: string };
    config.store.set({
      access: data.access,
      refresh: data.refresh ?? tokens.refresh,
    });
    return true;
  };

  const authFetch = async <T = unknown>(path: string, opts: AuthFetchOptions = {}): Promise<T> => {
    let response = await performRequest(path, opts);

    if (response.status === 401 && config.store.get()?.refresh) {
      const refreshed = await refreshTokens();
      if (refreshed) {
        response = await performRequest(path, opts);
      }
    }

    const text = await response.text();
    const payload: unknown = text ? safeJsonParse(text) : null;

    if (!response.ok) {
      throw new AuthFetchError(response.status, payload);
    }
    return payload as T;
  };

  return { authFetch, refreshTokens };
};

const safeJsonParse = (text: string): unknown => {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
};
