"use client";

import * as React from "react";

export type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  setTheme: (next: Theme) => void;
  toggle: () => void;
}

const ThemeContext = React.createContext<ThemeContextValue | null>(null);

const STORAGE_KEY = "offside-theme";

const readInitialTheme = (): Theme => {
  // SSR — return light. The inline script in app/layout.tsx overrides
  // the data-theme attribute synchronously on the client before paint,
  // so the SSR'd HTML never visibly flashes.
  if (typeof document === "undefined") return "light";
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr === "dark" || attr === "light") return attr;
  return "light";
};

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setThemeState] = React.useState<Theme>(readInitialTheme);

  const apply = React.useCallback((next: Theme) => {
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* private window, etc. — fall through */
    }
    setThemeState(next);
  }, []);

  const setTheme = React.useCallback(
    (next: Theme) => {
      apply(next);
    },
    [apply],
  );

  const toggle = React.useCallback(() => {
    apply(theme === "dark" ? "light" : "dark");
  }, [theme, apply]);

  // Keyboard shortcut: Cmd-Shift-D (macOS) / Ctrl-Shift-D (other) — toggle theme.
  // We skip when typing in an input so we don't fight with browser shortcuts
  // for "bookmark bar" etc., which usually require shift+ctrl/cmd alone.
  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const isToggle =
        (e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "d" || e.key === "D");
      if (!isToggle) return;
      const t = e.target as HTMLElement | null;
      const tag = t?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || t?.isContentEditable) return;
      e.preventDefault();
      toggle();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggle]);

  // React to OS theme changes — only when the user hasn't explicitly chosen
  // (i.e., no localStorage entry). If they've toggled, their preference wins.
  React.useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (e: MediaQueryListEvent) => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) apply(e.matches ? "dark" : "light");
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [apply]);

  const value = React.useMemo(() => ({ theme, setTheme, toggle }), [theme, setTheme, toggle]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextValue => {
  const ctx = React.useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within <ThemeProvider>");
  return ctx;
};
