"use client";

import { Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import * as React from "react";

import { useContacts, useCompanies, type Contact } from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

export default function ContactsListPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;

  return <ContactsList workspaceId={active.id} workspaceSlug={active.slug} />;
}

const ContactsList = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const contacts = useContacts(workspaceId);
  const companies = useCompanies(workspaceId);

  const companyById = React.useMemo(() => {
    const map = new Map<number, string>();
    (companies.data?.results ?? []).forEach((c) => map.set(c.id, c.name));
    return map;
  }, [companies.data]);

  return (
    <div className="container-editorial section-rhythm space-y-8 py-12">
      <header className="flex items-end justify-between gap-4">
        <div>
          <Eyebrow>Records</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            Contacts<span className="tan-period">.</span>
          </h1>
        </div>
        <Link
          href={`/${workspaceSlug}/contacts/new`}
          className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
        >
          + New contact
        </Link>
      </header>

      <Hairline />

      {contacts.isLoading ? (
        <p className="text-fg-muted">Loading contacts…</p>
      ) : (contacts.data?.results.length ?? 0) === 0 ? (
        <EmptyState workspaceSlug={workspaceSlug} />
      ) : (
        <div className="overflow-x-auto rounded-md border hairline">
          <table className="w-full text-sm">
            <thead className="bg-bone/60">
              <tr className="text-left">
                <Th>Name</Th>
                <Th>Email</Th>
                <Th>Title</Th>
                <Th>Company</Th>
                <Th>Stage</Th>
              </tr>
            </thead>
            <tbody className="divide-y hairline">
              {(contacts.data?.results ?? []).map((c) => (
                <ContactRow
                  key={c.id}
                  contact={c}
                  workspaceSlug={workspaceSlug}
                  companyName={c.company ? companyById.get(c.company) ?? "—" : "—"}
                />
              ))}
            </tbody>
          </table>
          <div className="border-t hairline px-4 py-2 font-mono text-[10px] text-fg-muted">
            Showing {contacts.data?.results.length ?? 0} of {contacts.data?.count ?? 0}
          </div>
        </div>
      )}
    </div>
  );
};

const Th = ({ children }: { children: React.ReactNode }) => (
  <th className="px-4 py-2 font-styrene text-[11px] uppercase tracking-eyebrow text-tan-text">
    {children}
  </th>
);

const ContactRow = ({
  contact,
  workspaceSlug,
  companyName,
}: {
  contact: Contact;
  workspaceSlug: string;
  companyName: string;
}) => {
  const fullName =
    `${contact.first_name} ${contact.last_name}`.trim() || contact.primary_email || "—";
  return (
    <tr className="hover:bg-tan-100/40">
      <td className="px-4 py-2">
        <Link
          href={`/${workspaceSlug}/contacts/${contact.id}`}
          className="font-medium hover:text-tan-text"
        >
          {fullName}
        </Link>
      </td>
      <td className="px-4 py-2 text-fg-muted">{contact.primary_email || "—"}</td>
      <td className="px-4 py-2 text-fg-muted">{contact.title || "—"}</td>
      <td className="px-4 py-2 text-fg-muted">{companyName}</td>
      <td className="px-4 py-2">
        {contact.lifecycle_stage ? (
          <StatusPill tone="neutral">{contact.lifecycle_stage}</StatusPill>
        ) : (
          <span className="text-fg-muted">—</span>
        )}
      </td>
    </tr>
  );
};

const EmptyState = ({ workspaceSlug }: { workspaceSlug: string }) => (
  <div className="rounded-md border hairline p-12 text-center">
    <Eyebrow>No contacts yet</Eyebrow>
    <h2 className="mt-2 text-2xl font-styrene font-bold">Bring your team into Offside.</h2>
    <p className="mt-3 text-fg-muted">
      Create one by hand, or import from CSV / HubSpot / Pipedrive (CSV import lands next).
    </p>
    <div className="mt-6 flex justify-center gap-3">
      <Link
        href={`/${workspaceSlug}/contacts/new`}
        className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700"
      >
        + New contact
      </Link>
    </div>
  </div>
);
