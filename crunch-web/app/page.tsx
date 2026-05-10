import { Eyebrow, Hairline, StatusPill } from "@offside/ui";

export default function HomePage() {
  return (
    <div className="container-editorial section-rhythm">
      <Eyebrow>Offside Studio · Product 02 · Letter X</Eyebrow>
      <h1 className="mt-4 text-5xl font-styrene font-bold tracking-tight md:text-7xl">
        Offside Crunch<span className="tan-period">.</span>
      </h1>
      <p className="mt-6 max-w-2xl text-lg leading-relaxed text-fg-muted">
        AI-native spreadsheet. Built on the same brand tokens, auth stack, AI infra, and workflow
        primitives as Offside CRM. Coming after CRM ships.
      </p>
      <div className="mt-8 flex flex-wrap items-center gap-3">
        <StatusPill tone="info">Placeholder · M0 phase 2</StatusPill>
        <span className="font-mono text-xs text-fg-muted">port 3001</span>
      </div>
      <Hairline className="mt-12" />
      <p className="mt-12 max-w-2xl text-sm text-fg-muted">
        This page exists to prove the suite-shape of <code>packages/ui</code>. When Crunch begins,
        this app gets real chrome — same tokens, distinct secondary accent (warm wheat).
      </p>
    </div>
  );
}
