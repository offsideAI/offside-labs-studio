"use client";

import { useParams } from "next/navigation";
import * as React from "react";

import { useKeyboardShortcut } from "../lib/keyboard";
import { useActiveWorkspace } from "../lib/contexts";
import { CommandPalette } from "./command-palette";
import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";

export const AppShell = ({ children }: { children: React.ReactNode }) => {
  const { active, workspaces } = useActiveWorkspace();
  const params = useParams<{ workspace: string }>();
  const [paletteOpen, setPaletteOpen] = React.useState(false);

  useKeyboardShortcut("k", () => setPaletteOpen((v) => !v), { meta: true });
  useKeyboardShortcut("/", () => setPaletteOpen(true));
  useKeyboardShortcut("Escape", () => setPaletteOpen(false), { allowInInput: true });

  return (
    <div className="flex min-h-screen">
      <Sidebar workspaceName={active?.name ?? "Workspace"} />
      <div className="flex flex-1 flex-col">
        <TopBar onSearchClick={() => setPaletteOpen(true)} />
        <div className="flex-1">{children}</div>
      </div>
      <CommandPalette
        open={paletteOpen}
        onOpenChange={setPaletteOpen}
        workspaces={workspaces}
        activeSlug={params.workspace}
      />
    </div>
  );
};
