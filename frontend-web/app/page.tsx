import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container-editorial section-rhythm">
      <Eyebrow>Offside Studio · Product 01</Eyebrow>
      <h1 className="mt-4 text-5xl font-styrene font-bold tracking-tight md:text-7xl">
        OffsideStudio<span className="tan-period">.</span>
      </h1>
      <p className="mt-2 max-w-2xl text-2xl font-styrene font-bold leading-tight text-tan-text md:text-3xl">
        Agent Marketplace.
      </p>
      <p className="mt-6 max-w-2xl text-lg leading-relaxed text-fg-muted">
        Install a pre-built agent. Watch it deploy your entire ecommerce funnel — marketing campaign
        launch, AEO content, ads, landing pages, email, cart recovery, payments — against your CRM.
        Customize every step in the Agent Design Studio. Every lead pulled into the funnel becomes a
        tracked conversion.
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-4">
        <Link
          href="/brand"
          className="inline-flex h-10 items-center justify-center rounded-sm border border-ink bg-ink px-4 text-sm font-styrene font-bold text-bone transition-colors duration-200 hover:bg-ink-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
        >
          View brand tokens
        </Link>
        <span className="font-mono text-xs text-fg-muted">
          M0 phase 2 · scaffold in progress
        </span>
      </div>

      <Hairline className="mt-16" />

      <section className="mt-12">
        <Eyebrow>What ships at MVP</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          One click installs your entire ecommerce funnel.
        </h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <Eyebrow>Wedge 01</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">Agent Marketplace.</h3>
            </CardHeader>
            <CardContent>
              <p className="text-fg-muted">
                A curated catalog of pre-built agents spanning the full ecommerce lifecycle — lead
                capture, cart recovery, fulfillment, payments, customer service. Install one with a
                click. Or describe one in English and let Claude generate it. Durable execution on
                Celery + a custom Django layer.
              </p>
              <StatusPill tone="info">Milestones M7–M9</StatusPill>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Eyebrow>Wedge 02</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">Conversational data.</h3>
            </CardHeader>
            <CardContent>
              <p className="text-fg-muted">
                Natural-language queries across every record, every email, every note. Hybrid
                keyword + pgvector rerank. Schema-aware prompting, including custom fields.
              </p>
              <StatusPill tone="info">Milestone M12</StatusPill>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Eyebrow>Wedge 03</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">Agent autonomy with HITL.</h3>
            </CardHeader>
            <CardContent>
              <p className="text-fg-muted">
                Default-suggest, opt-in autonomous per action type. Human-in-the-loop approval via
                in-app inbox, email magic-link, or iOS push from the lock screen.
              </p>
              <StatusPill tone="info">Milestone M13</StatusPill>
            </CardContent>
          </Card>
        </div>
      </section>

      <Hairline className="mt-16" />

      <footer className="mt-12 grid gap-4 text-sm text-fg-muted md:grid-cols-2">
        <p>
          Part of the{" "}
          <a href="https://platform.offside.ai" className="link-tan">
            Offside Studio Suite
          </a>
          . Engineer-to-engineer. Proudly open by design.
        </p>
        <p className="md:text-right">
          See <Link href="/brand" className="link-tan">brand tokens</Link>,{" "}
          <a href="https://github.com/" className="link-tan">
            roadmap
          </a>
          , and the source-of-truth docs in <code>PLAN.md</code>.
        </p>
      </footer>
    </div>
  );
}
