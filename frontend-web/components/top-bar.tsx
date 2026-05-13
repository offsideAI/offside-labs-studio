"use client";

import * as React from "react";

import { useTheme } from "../lib/theme";

import { WorkspaceSwitcher } from "./workspace-switcher";

interface TopBarProps {
  onSearchClick: () => void;
}

export const TopBar = ({ onSearchClick }: TopBarProps) => {
  const [shortcutLabel, setShortcutLabel] = React.useState("Ctrl K");
  const [themeShortcut, setThemeShortcut] = React.useState("Ctrl Shift D");
  React.useEffect(() => {
    if (typeof navigator !== "undefined" && /Mac/i.test(navigator.userAgent)) {
      setShortcutLabel("⌘ K");
      setThemeShortcut("⌘ ⇧ D");
    }
  }, []);

  return (
    <header className="border-b hairline bg-bone/80 backdrop-blur sticky top-0 z-10">
      <div className="flex h-14 items-center justify-between gap-4 px-6">
        <div className="flex items-center gap-3">
          <span className="font-styrene font-bold">OffsideStudio</span>
          <span className="text-fg-muted">/</span>
          <WorkspaceSwitcher />
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onSearchClick}
            aria-label="Open command palette"
            className="inline-flex h-8 items-center gap-2 rounded-sm border hairline bg-bone px-3 text-xs text-fg-muted hover:bg-tan-100 dark:hover:bg-[var(--surface-overlay)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          >
            <span>Search workspaces, settings…</span>
            <kbd className="rounded-sm border hairline bg-bone px-1 py-0.5 font-mono text-[10px]">
              {shortcutLabel}
            </kbd>
          </button>
          <ThemeToggle shortcut={themeShortcut} />
        </div>
      </div>
    </header>
  );
};

// Subtle pill-style theme toggle. Sun in light mode → moon in dark mode.
// Click cycles; Cmd-Shift-D also cycles (registered globally in ThemeProvider).
const ThemeToggle = ({ shortcut }: { shortcut: string }) => {
  const { theme, toggle } = useTheme();
  return (
    <button
      type="button"
      onClick={toggle}
      title={`Toggle theme (${shortcut})`}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className="inline-flex h-8 w-8 items-center justify-center rounded-full border hairline bg-bone text-fg-muted transition-all duration-200 hover:border-tan hover:text-ink dark:hover:bg-[var(--surface-overlay)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
    >
      {theme === "dark" ? <SunIcon /> : <MoonIcon />}
    </button>
  );
};

const SunIcon = () => (
  <svg aria-hidden className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3.5" />
    <path d="M12 3v2" />
    <path d="M12 19v2" />
    <path d="M3 12h2" />
    <path d="M19 12h2" />
    <path d="M5.6 5.6l1.4 1.4" />
    <path d="M17 17l1.4 1.4" />
    <path d="M5.6 18.4l1.4-1.4" />
    <path d="M17 7l1.4-1.4" />
  </svg>
);

const MoonIcon = () => (
  <svg aria-hidden className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
  </svg>
);
