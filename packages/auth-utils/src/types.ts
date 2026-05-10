// Shared types for the auth surface — kept in their own module so tokens.ts
// and authFetch.ts can import without a circular dependency on index.ts.

export interface OffsideJwtPayload {
  user_id: number;
  email: string;
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

export interface AuthFetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  workspaceId?: number | null;
}

export interface AuthFetchConfig {
  baseUrl: string;
  store: TokenStore;
  refreshPath?: string;
  onAuthFailure?: () => void;
}

export class AuthFetchError extends Error {
  constructor(
    public status: number,
    public payload: unknown,
    message?: string,
  ) {
    super(message ?? `Auth fetch failed: ${status}`);
    this.name = "AuthFetchError";
  }
}
