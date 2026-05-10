"use client";

import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import {
  useCompany,
  useContact,
  useDeal,
  useDeleteDeal,
  usePipelines,
  useUpdateDeal,
} from "../../../../lib/api";
import { useActiveWorkspace } from "../../../../lib/contexts";
import { ActivityFeed } from "../../../../components/activity-feed";
import { NotesTab } from "../../../../components/notes-tab";
import { TasksTab } from "../../../../components/tasks-tab";

export default function DealDetailPage() {
  const params = useParams<{ workspace: string; id: string }>();
  const { active } = useActiveWorkspace();
  if (!active) return null;
  return (
    <DealDetail
      workspaceId={active.id}
      workspaceSlug={params.workspace}
      dealId={params.id}
    />
  );
}

const DealDetail = ({
  workspaceId,
  workspaceSlug,
  dealId,
}: {
  workspaceId: number;
  workspaceSlug: string;
  dealId: string;
}) => {
  const router = useRouter();
  const deal = useDeal(workspaceId, dealId);
  const update = useUpdateDeal(workspaceId);
  const remove = useDeleteDeal(workspaceId);
  const pipelines = usePipelines(workspaceId);
  const contact = useContact(workspaceId, deal.data?.contact ?? "");
  const company = useCompany(workspaceId, deal.data?.company ?? "");

  if (deal.isLoading || !deal.data) {
    return (
      <div className="container-editorial py-12">
        <p className="text-fg-muted">Loading deal…</p>
      </div>
    );
  }

  const d = deal.data;
  const pipeline = (pipelines.data?.results ?? []).find((p) => p.id === d.pipeline);
  const stage = pipeline?.stages.find((s) => s.id === d.stage_id);

  const onStageChange = (stageId: string) => {
    update.mutate({ id: d.id, patch: { stage_id: stageId } });
  };

  const onArchive = async () => {
    if (!window.confirm("Archive this deal?")) return;
    await remove.mutateAsync(d.id);
    router.replace(`/${workspaceSlug}/deals`);
  };

  const valueDisplay = new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: d.currency || "USD",
    maximumFractionDigits: 0,
  }).format(d.value_cents / 100);

  return (
    <div className="container-editorial space-y-10 py-12">
      <div>
        <Link href={`/${workspaceSlug}/deals`} className="link-tan text-sm">
          ← Deals
        </Link>
      </div>

      <header className="flex items-start justify-between gap-4">
        <div>
          <Eyebrow>Deal · #{d.id}</Eyebrow>
          <h1 className="mt-2 text-4xl font-styrene font-bold tracking-tight md:text-5xl">
            {d.name}<span className="tan-period">.</span>
          </h1>
          <p className="mt-2 text-fg-muted">
            {valueDisplay} · {pipeline?.name ?? "—"}
            {stage ? (
              <>
                {" · "}
                <StatusPill tone="neutral">{stage.label}</StatusPill>
              </>
            ) : null}
          </p>
        </div>
        <button
          onClick={onArchive}
          disabled={remove.isPending}
          className="rounded-sm border border-[#8E3B30] bg-transparent px-4 py-2 text-sm font-medium text-[#8E3B30] hover:bg-[#F4DEDA]"
        >
          Archive
        </button>
      </header>

      <Hairline />

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_320px]">
        <main className="space-y-8">
          <Card>
            <CardHeader>
              <Eyebrow>Stage</Eyebrow>
              <h2 className="text-xl font-styrene font-bold">Move through the pipeline.</h2>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(pipeline?.stages ?? [])
                  .slice()
                  .sort((a, b) => a.order - b.order)
                  .map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => onStageChange(s.id)}
                      className={
                        "rounded-sm border px-3 py-1.5 text-sm transition-colors " +
                        (s.id === d.stage_id
                          ? "border-ink bg-ink text-bone"
                          : "hairline bg-bone text-ink hover:bg-tan-100")
                      }
                    >
                      {s.label}
                    </button>
                  ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Eyebrow>Tasks</Eyebrow>
              <h2 className="text-xl font-styrene font-bold">Things to do.</h2>
            </CardHeader>
            <CardContent>
              <TasksTab relatedType="deal" relatedId={d.id} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Eyebrow>Notes</Eyebrow>
              <h2 className="text-xl font-styrene font-bold">What you&rsquo;re thinking.</h2>
            </CardHeader>
            <CardContent>
              <NotesTab relatedType="deal" relatedId={d.id} />
            </CardContent>
          </Card>
        </main>

        <aside className="space-y-6">
          <Card>
            <CardHeader>
              <Eyebrow>Linked</Eyebrow>
              <h2 className="text-base font-styrene font-bold">Records.</h2>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <Pair label="Contact">
                {contact.data ? (
                  <Link
                    href={`/${workspaceSlug}/contacts/${contact.data.id}`}
                    className="link-tan"
                  >
                    {`${contact.data.first_name} ${contact.data.last_name}`.trim() ||
                      contact.data.primary_email}
                  </Link>
                ) : (
                  "—"
                )}
              </Pair>
              <Pair label="Company">
                {company.data ? (
                  <Link
                    href={`/${workspaceSlug}/companies/${company.data.id}`}
                    className="link-tan"
                  >
                    {company.data.name}
                  </Link>
                ) : (
                  "—"
                )}
              </Pair>
              <Pair label="Expected close">
                {d.expected_close ? new Date(d.expected_close).toLocaleDateString() : "—"}
              </Pair>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Eyebrow>Activity</Eyebrow>
              <h2 className="text-base font-styrene font-bold">Recent.</h2>
            </CardHeader>
            <CardContent>
              <ActivityFeed relatedType="deal" relatedId={d.id} />
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
};

const Pair = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div>
    <dt className="text-[10px] font-mono uppercase tracking-eyebrow text-tan-text">{label}</dt>
    <dd className="mt-0.5">{children}</dd>
  </div>
);
