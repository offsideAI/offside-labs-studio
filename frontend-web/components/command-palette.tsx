"use client";

import { Command } from "cmdk";
import { useRouter } from "next/navigation";
import * as React from "react";

import { apiTokens, useLogout, type Workspace } from "../lib/api";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspaces: Workspace[];
  activeSlug?: string;
}

export const CommandPalette = ({ open, onOpenChange, workspaces, activeSlug }: CommandPaletteProps) => {
  const router = useRouter();
  const logout = useLogout();

  const close = React.useCallback(() => onOpenChange(false), [onOpenChange]);

  const navigate = React.useCallback(
    (path: string) => {
      router.push(path);
      close();
    },
    [router, close],
  );

  const onSignOut = React.useCallback(async () => {
    close();
    await logout.mutateAsync();
    apiTokens.clear();
    router.replace("/login");
  }, [close, logout, router]);

  return (
    <Command.Dialog
      open={open}
      onOpenChange={onOpenChange}
      label="Command palette"
      className="cmdk-dialog"
    >
      <Command.Input placeholder="Type a command or search workspaces…" className="cmdk-input" />
      <Command.List className="cmdk-list">
        <Command.Empty className="cmdk-empty">No matching commands.</Command.Empty>

        {activeSlug ? (
          <Command.Group heading="Navigate" className="cmdk-group">
            <Command.Item onSelect={() => navigate(`/${activeSlug}`)} className="cmdk-item">
              <span>Home</span>
              <span className="cmdk-hint">{`/${activeSlug}`}</span>
            </Command.Item>
            <Command.Item onSelect={() => navigate(`/${activeSlug}/contacts`)} className="cmdk-item">
              <span>Contacts</span>
              <span className="cmdk-hint">{`/${activeSlug}/contacts`}</span>
            </Command.Item>
            <Command.Item onSelect={() => navigate(`/${activeSlug}/companies`)} className="cmdk-item">
              <span>Companies</span>
              <span className="cmdk-hint">{`/${activeSlug}/companies`}</span>
            </Command.Item>
            <Command.Item onSelect={() => navigate(`/${activeSlug}/deals`)} className="cmdk-item">
              <span>Deals</span>
              <span className="cmdk-hint">{`/${activeSlug}/deals`}</span>
            </Command.Item>
            <Command.Item onSelect={() => navigate(`/${activeSlug}/settings`)} className="cmdk-item">
              <span>Settings</span>
              <span className="cmdk-hint">{`/${activeSlug}/settings`}</span>
            </Command.Item>
            <Command.Item
              onSelect={() => navigate(`/${activeSlug}/settings/custom-fields`)}
              className="cmdk-item"
            >
              <span>Custom fields</span>
              <span className="cmdk-hint">{`/${activeSlug}/settings/custom-fields`}</span>
            </Command.Item>
            <Command.Item onSelect={() => navigate("/brand")} className="cmdk-item">
              <span>Brand tokens</span>
              <span className="cmdk-hint">/brand</span>
            </Command.Item>
          </Command.Group>
        ) : null}

        {workspaces.length > 0 ? (
          <Command.Group heading="Switch workspace" className="cmdk-group">
            {workspaces.map((ws) => (
              <Command.Item
                key={ws.id}
                value={`workspace ${ws.name} ${ws.slug}`}
                onSelect={() => navigate(`/${ws.slug}`)}
                className="cmdk-item"
              >
                <span>{ws.name}</span>
                <span className="cmdk-hint">/{ws.slug}</span>
              </Command.Item>
            ))}
            <Command.Item onSelect={() => navigate("/onboarding")} className="cmdk-item">
              <span>+ New workspace</span>
            </Command.Item>
          </Command.Group>
        ) : null}

        <Command.Group heading="Account" className="cmdk-group">
          <Command.Item onSelect={onSignOut} className="cmdk-item">
            <span>Sign out</span>
          </Command.Item>
        </Command.Group>
      </Command.List>

      <style jsx global>{`
        [cmdk-overlay] {
          position: fixed;
          inset: 0;
          background: rgba(30, 30, 30, 0.4);
          z-index: 50;
        }
        .cmdk-dialog {
          position: fixed;
          top: 12vh;
          left: 50%;
          transform: translateX(-50%);
          width: min(640px, calc(100vw - 32px));
          background: var(--brand-bone);
          border: 1px solid var(--brand-rule);
          border-radius: 12px;
          box-shadow: 0 16px 48px rgba(30, 30, 30, 0.18);
          z-index: 60;
          overflow: hidden;
        }
        .cmdk-input {
          width: 100%;
          padding: 16px 20px;
          background: transparent;
          border: 0;
          border-bottom: 1px solid var(--brand-rule);
          color: var(--brand-ink);
          font-family: var(--font-roboto), system-ui, sans-serif;
          font-size: 0.95rem;
          outline: none;
        }
        .cmdk-input::placeholder {
          color: var(--brand-muted);
        }
        .cmdk-list {
          max-height: 360px;
          overflow-y: auto;
          padding: 8px;
        }
        .cmdk-empty {
          padding: 24px;
          text-align: center;
          color: var(--brand-muted);
          font-size: 0.875rem;
        }
        .cmdk-group [cmdk-group-heading] {
          padding: 8px 12px 4px;
          font-family: var(--font-styrene), system-ui, sans-serif;
          font-size: 0.625rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.18em;
          color: var(--brand-tan-text);
        }
        .cmdk-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 12px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
          color: var(--brand-ink);
          gap: 12px;
        }
        .cmdk-item[data-selected="true"] {
          background: var(--brand-tan);
          color: var(--brand-ink);
        }
        .cmdk-hint {
          font-family: var(--font-jetbrains), ui-monospace, monospace;
          font-size: 0.7rem;
          color: var(--brand-muted);
        }
        .cmdk-item[data-selected="true"] .cmdk-hint {
          color: rgba(30, 30, 30, 0.72);
        }
      `}</style>
    </Command.Dialog>
  );
};
