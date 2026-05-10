// @offside/auth-utils — JWT helpers and fetch interceptors.
//
// The Django backend (see backend/apps/users/) is the auth source of truth.
// This package mirrors the JWT contract so web + iOS frontends agree on
// payload shape and refresh semantics.
//
// Real implementations land in M2 alongside the workspace + invite flow.

export interface OffsideJwtPayload {
  sub: string; // user id
  email: string;
  active_workspace_id: string | null;
  exp: number;
  iat: number;
}

export type Tokens = {
  access: string;
  refresh: string;
};

export type TokenStore = {
  get(): Tokens | null;
  set(tokens: Tokens): void;
  clear(): void;
};

// Stubs — wired up in M2.
export const memoryTokenStore = (): TokenStore => {
  let tokens: Tokens | null = null;
  return {
    get: () => tokens,
    set: (next) => {
      tokens = next;
    },
    clear: () => {
      tokens = null;
    },
  };
};

export interface AuthFetchOptions extends RequestInit {
  store: TokenStore;
  refreshUrl: string;
}

export async function authFetch(_input: RequestInfo | URL, _init: AuthFetchOptions): Promise<Response> {
  throw new Error("authFetch is not implemented yet — wired up in M2.");
}
