"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";

import { useWorkspaces, type Workspace } from "./api";

interface WorkspaceContextValue {
  active: Workspace | null;
  isLoading: boolean;
  workspaces: Workspace[];
}

const WorkspaceContext = React.createContext<WorkspaceContextValue | null>(null);

export const WorkspaceProvider = ({ children }: { children: React.ReactNode }) => {
  const params = useParams<{ workspace?: string }>();
  const slug = params.workspace;
  const { data, isLoading } = useWorkspaces();

  const workspaces = data?.results ?? [];
  const active = slug ? (workspaces.find((w) => w.slug === slug) ?? null) : null;

  const value = React.useMemo<WorkspaceContextValue>(
    () => ({ active, isLoading, workspaces }),
    [active, isLoading, workspaces],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
};

export const useActiveWorkspace = (): WorkspaceContextValue => {
  const value = React.useContext(WorkspaceContext);
  if (!value) {
    throw new Error("useActiveWorkspace must be used inside <WorkspaceProvider>");
  }
  return value;
};

// --- AuthGate: client-side redirect if no session ---

export const AuthGate = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const [checked, setChecked] = React.useState(false);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    const hasSession = window.localStorage.getItem("offside.access");
    if (!hasSession) {
      router.replace("/login");
    } else {
      setChecked(true);
    }
  }, [router]);

  if (!checked) return null;
  return <>{children}</>;
};
