"use client";

import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { useWorkspaces } from "../../lib/api";
import { AuthGate, WorkspaceProvider, useActiveWorkspace } from "../../lib/contexts";
import { WorkspaceSwitcher } from "../../components/workspace-switcher";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <WorkspaceProvider>
        <WorkspaceShell>{children}</WorkspaceShell>
      </WorkspaceProvider>
    </AuthGate>
  );
}

const WorkspaceShell = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const params = useParams<{ workspace: string }>();
  const workspaces = useWorkspaces();
  const { active, isLoading } = useActiveWorkspace();

  React.useEffect(() => {
    if (workspaces.isLoading || isLoading) return;
    const list = workspaces.data?.results ?? [];
    if (list.length === 0) {
      router.replace("/onboarding");
      return;
    }
    if (!list.find((w) => w.slug === params.workspace)) {
      router.replace(`/${list[0]?.slug ?? ""}`);
    }
  }, [params.workspace, workspaces.data, workspaces.isLoading, isLoading, router]);

  if (workspaces.isLoading || !active) {
    return (
      <div className="container-editorial section-rhythm">
        <p className="text-fg-muted">Loading workspace…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b hairline bg-bone/80 backdrop-blur sticky top-0 z-10">
        <div className="container-editorial flex h-14 items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-styrene font-bold">Offside CRM</span>
            <span className="text-fg-muted">/</span>
            <WorkspaceSwitcher />
          </div>
          <div className="text-xs text-fg-muted font-mono">
            M2 · workspace shell · cmd-K + nav land in M3
          </div>
        </div>
      </header>
      {children}
    </div>
  );
};
