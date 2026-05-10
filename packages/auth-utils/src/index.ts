// @offside/auth-utils — JWT helpers, token storage, and a fetch wrapper that
// auto-attaches Bearer auth + the X-Workspace-Id header and transparently
// refreshes on 401.
//
// Used by frontend-web (M2+) and frontend-ios via a thin Swift wrapper (M6).
// The Django backend at /api/auth/* is the auth source of truth (PLAN.md §5).

export {
  AuthFetchError,
  type AuthFetchConfig,
  type AuthFetchOptions,
  type OffsideJwtPayload,
  type Tokens,
  type TokenStore,
} from "./types";

export { browserTokenStore, memoryTokenStore } from "./tokens";
export { createAuthFetch } from "./authFetch";
