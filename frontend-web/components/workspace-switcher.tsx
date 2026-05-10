"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import { apiTokens, useLogout } from "../lib/api";
import { useActiveWorkspace } from "../lib/contexts";

export const WorkspaceSwitcher = () => {
  const router = useRouter();
  const { active, workspaces } = useActiveWorkspace();
  const logout = useLogout();
  const [open, setOpen] = React.useState(false);

  const ref = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    const onClick = (event: MouseEvent) => {
      if (!ref.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const handleLogout = async () => {
    await logout.mutateAsync();
    apiTokens.clear();
    router.replace("/login");
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-1.5 rounded-sm px-2 py-1 text-sm font-medium hover:bg-tan-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <span>{active?.name ?? "Workspace"}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          aria-hidden
        >
          <path d="M2.5 4.5L6 8l3.5-3.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open ? (
        <div
          role="menu"
          className="absolute left-0 top-full mt-1 min-w-[240px] rounded-md border hairline bg-bone p-1 shadow-soft-2"
        >
          <p className="px-3 py-2 font-mono text-[10px] uppercase tracking-eyebrow text-tan-text">
            Switch workspace
          </p>
          {workspaces.map((w) => (
            <Link
              key={w.id}
              href={`/${w.slug}`}
              role="menuitem"
              className="block rounded-sm px-3 py-2 text-sm hover:bg-tan-100"
              onClick={() => setOpen(false)}
            >
              {w.name}
              <span className="ml-2 font-mono text-xs text-fg-muted">{w.slug}</span>
            </Link>
          ))}
          <hr className="my-1 hairline" />
          <Link
            href="/onboarding"
            className="block rounded-sm px-3 py-2 text-sm hover:bg-tan-100"
            onClick={() => setOpen(false)}
          >
            + New workspace
          </Link>
          <button
            type="button"
            onClick={handleLogout}
            className="block w-full rounded-sm px-3 py-2 text-left text-sm hover:bg-tan-100"
          >
            Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
};
