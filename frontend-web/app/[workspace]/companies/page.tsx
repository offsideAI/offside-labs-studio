"use client";

import { Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";

import { useCompanies, type Company } from "../../../lib/api";
import { useActiveWorkspace } from "../../../lib/contexts";

export default function CompaniesListPage() {
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return <CompaniesList workspaceId={active.id} workspaceSlug={active.slug} />;
}

const CompaniesList = ({
  workspaceId,
  workspaceSlug,
}: {
  workspaceId: number;
  workspaceSlug: string;
}) => {
  const companies = useCompanies(workspaceId);

  return (
    <div className="container-editorial section-rhythm space-y-8 py-12">
      <header className="flex items-end justify-between gap-4">
        <div>
          <Eyebrow>Records</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            Companies<span className="tan-period">.</span>
          </h1>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/${workspaceSlug}/companies/import`}
            className="inline-flex h-10 items-center rounded-sm border hairline bg-bone px-4 text-sm font-medium hover:bg-tan-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          >
            Import CSV
          </Link>
          <Link
            href={`/${workspaceSlug}/companies/new`}
            className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          >
            + New company
          </Link>
        </div>
      </header>

      <Hairline />

      {companies.isLoading ? (
        <p className="text-fg-muted">Loading companies…</p>
      ) : (companies.data?.results.length ?? 0) === 0 ? (
        <div className="rounded-md border hairline p-12 text-center">
          <Eyebrow>No companies yet</Eyebrow>
          <h2 className="mt-2 text-2xl font-styrene font-bold">Add the orgs you sell to.</h2>
          <p className="mt-3 text-fg-muted">
            Companies are the parent record for contacts and (later) deals.
          </p>
          <div className="mt-6">
            <Link
              href={`/${workspaceSlug}/companies/new`}
              className="inline-flex h-10 items-center rounded-sm border border-ink bg-ink px-4 text-sm font-bold text-bone hover:bg-ink-700"
            >
              + New company
            </Link>
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-md border hairline">
          <table className="w-full text-sm">
            <thead className="bg-bone/60">
              <tr className="text-left">
                <Th>Name</Th>
                <Th>Domain</Th>
                <Th>Industry</Th>
                <Th>Size</Th>
              </tr>
            </thead>
            <tbody className="divide-y hairline">
              {(companies.data?.results ?? []).map((c) => (
                <CompanyRow key={c.id} company={c} workspaceSlug={workspaceSlug} />
              ))}
            </tbody>
          </table>
          <div className="border-t hairline px-4 py-2 font-mono text-[10px] text-fg-muted">
            Showing {companies.data?.results.length ?? 0} of {companies.data?.count ?? 0}
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

const CompanyRow = ({
  company,
  workspaceSlug,
}: {
  company: Company;
  workspaceSlug: string;
}) => (
  <tr className="hover:bg-tan-100/40">
    <td className="px-4 py-2">
      <Link
        href={`/${workspaceSlug}/companies/${company.id}`}
        className="font-medium hover:text-tan-text"
      >
        {company.name}
      </Link>
    </td>
    <td className="px-4 py-2 text-fg-muted">{company.domain || "—"}</td>
    <td className="px-4 py-2 text-fg-muted">{company.industry || "—"}</td>
    <td className="px-4 py-2">
      {company.size_band ? (
        <StatusPill tone="neutral">{company.size_band}</StatusPill>
      ) : (
        <span className="text-fg-muted">—</span>
      )}
    </td>
  </tr>
);
