"use client";

import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { useWorkspaces } from "../../lib/api";
import { AuthGate, WorkspaceProvider, useActiveWorkspace } from "../../lib/contexts";
import { AppShell } from "../../components/app-shell";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <WorkspaceProvider>
        <WorkspaceShellGate>{children}</WorkspaceShellGate>
      </WorkspaceProvider>
    </AuthGate>
  );
}

const WorkspaceShellGate = ({ children }: { children: React.ReactNode }) => {
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
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-fg-muted">Loading workspace…</p>
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
};
