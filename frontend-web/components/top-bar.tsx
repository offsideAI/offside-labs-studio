"use client";

import * as React from "react";

import { WorkspaceSwitcher } from "./workspace-switcher";

interface TopBarProps {
  onSearchClick: () => void;
}

export const TopBar = ({ onSearchClick }: TopBarProps) => {
  const [shortcutLabel, setShortcutLabel] = React.useState("Ctrl K");
  React.useEffect(() => {
    if (typeof navigator !== "undefined" && /Mac/i.test(navigator.userAgent)) {
      setShortcutLabel("⌘ K");
    }
  }, []);

  return (
    <header className="border-b hairline bg-bone/80 backdrop-blur sticky top-0 z-10">
      <div className="flex h-14 items-center justify-between gap-4 px-6">
        <div className="flex items-center gap-3">
          <span className="font-styrene font-bold">Offside CRM</span>
          <span className="text-fg-muted">/</span>
          <WorkspaceSwitcher />
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onSearchClick}
            aria-label="Open command palette"
            className="inline-flex h-8 items-center gap-2 rounded-sm border hairline bg-bone px-3 text-xs text-fg-muted hover:bg-tan-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          >
            <span>Search workspaces, settings…</span>
            <kbd className="rounded-sm border hairline bg-bone px-1 py-0.5 font-mono text-[10px]">
              {shortcutLabel}
            </kbd>
          </button>
        </div>
      </div>
    </header>
  );
};
