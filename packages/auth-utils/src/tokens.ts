// Token storage abstractions. Web uses localStorage for refresh + memory for access.
// iOS will implement the same interface backed by Keychain in M6.

import type { Tokens, TokenStore } from "./types";

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

const REFRESH_KEY = "offside.refresh";
const ACCESS_KEY = "offside.access";

export const browserTokenStore = (): TokenStore => {
  if (typeof window === "undefined") {
    // SSR: fall through to a memory store; client takes over on hydrate.
    return memoryTokenStore();
  }
  return {
    get: () => {
      const access = window.localStorage.getItem(ACCESS_KEY);
      const refresh = window.localStorage.getItem(REFRESH_KEY);
      if (!access || !refresh) return null;
      return { access, refresh };
    },
    set: (next) => {
      window.localStorage.setItem(ACCESS_KEY, next.access);
      window.localStorage.setItem(REFRESH_KEY, next.refresh);
    },
    clear: () => {
      window.localStorage.removeItem(ACCESS_KEY);
      window.localStorage.removeItem(REFRESH_KEY);
    },
  };
};
