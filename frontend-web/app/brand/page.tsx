import {
  Button,
  Card,
  CardContent,
  CardHeader,
  Eyebrow,
  Hairline,
  StatusPill,
} from "@offside/ui";
import Link from "next/link";

export default function BrandPage() {
  return (
    <div className="container-editorial section-rhythm space-y-20">
      <header>
        <Eyebrow>OffsideAI Design System v1.0</Eyebrow>
        <h1 className="mt-4 text-5xl font-styrene font-bold tracking-tight md:text-7xl">
          Brand tokens<span className="tan-period">.</span>
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-fg-muted">
          Source of truth for color, type, spacing, and component primitives across the Offside
          Studio Suite. Tokens are adopted verbatim from the offside.ai marketing site. Tan is
          emphasis only. Saturated blue, purple, and cyan are off-brand.
        </p>
        <div className="mt-6">
          <Link href="/" className="link-tan">
            ← Back to home
          </Link>
        </div>
      </header>

      <Hairline />

      <section>
        <Eyebrow>01 · Color</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          Tan, Ink, Bone.
        </h2>
        <p className="mt-3 max-w-2xl text-fg-muted">
          The brand is a three-color palette. Every other color is a derived warm-neutral or a
          muted status signal — never an unrelated accent.
        </p>
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Swatch name="--brand-tan" hex="#C9A389" labelTone="dark" />
          <Swatch name="--brand-ink" hex="#1E1E1E" labelTone="light" />
          <Swatch name="--brand-bone" hex="#F1F1F1" labelTone="dark" />
          <Swatch name="--brand-tan-text" hex="#7A5F44" labelTone="light" />
        </div>
        <p className="mt-4 max-w-2xl text-sm text-fg-muted">
          The brand book listed <code>#B8916F</code> for tan-on-bone copy; that fails WCAG (2.54:1
          on Bone). The token here is corrected to <code>#7A5F44</code> per the production CSS.
        </p>
      </section>

      <Hairline />

      <section>
        <Eyebrow>02 · Type</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          Display · Body · Mono.
        </h2>
        <p className="mt-3 max-w-2xl text-fg-muted">
          Display is Styrene A (paid Commercial Type) with a Söhne → Inter fallback. Until Styrene
          A is licensed and dropped into <code>frontend-web/public/fonts/</code>, the page falls
          through that chain.
        </p>
        <div className="mt-8 space-y-6">
          <p className="text-7xl font-styrene font-bold tracking-tight">
            Display XL<span className="tan-period">.</span>
          </p>
          <p className="text-5xl font-styrene font-bold tracking-tight">Display L.</p>
          <p className="text-3xl font-styrene font-bold">H2 — sentence case.</p>
          <p className="text-xl font-styrene font-bold">H3</p>
          <Eyebrow>Eyebrow · 0.18em tracked · uppercase</Eyebrow>
          <p className="font-sans text-base">
            Body — Roboto. Engineer-to-engineer voice. Two short clauses. No adjective inflation.
          </p>
          <p className="font-mono text-sm">
            Mono — JetBrains Mono · <span className="text-tan">0xC9A389</span>
          </p>
        </div>
      </section>

      <Hairline />

      <section>
        <Eyebrow>03 · Spacing & surface</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          4px base · six radius steps · soft warm shadows.
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <Eyebrow>Radii</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">2 · 4 · 8 · 12 · 16 · pill.</h3>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-end gap-3">
                {(["none", "xs", "sm", "md", "lg", "xl", "2xl", "full"] as const).map((r) => (
                  <div
                    key={r}
                    className="flex h-16 w-16 items-center justify-center bg-tan-100"
                    style={{
                      borderRadius:
                        r === "none"
                          ? 0
                          : r === "xs"
                            ? 2
                            : r === "sm"
                              ? 4
                              : r === "md"
                                ? 8
                                : r === "lg"
                                  ? 12
                                  : r === "xl"
                                    ? 16
                                    : r === "2xl"
                                      ? 20
                                      : 9999,
                    }}
                  >
                    <span className="font-mono text-xs text-tan-text">{r}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Eyebrow>Shadows</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">Never dramatic.</h3>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {(["soft-1", "soft-2", "soft-3", "soft-4"] as const).map((s) => (
                  <div
                    key={s}
                    className={`flex h-16 items-center justify-center rounded-md bg-bone shadow-${s}`}
                  >
                    <span className="font-mono text-xs text-fg-muted">{s}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Eyebrow>Container</Eyebrow>
              <h3 className="text-xl font-styrene font-bold">1280 max · 88px gutters.</h3>
            </CardHeader>
            <CardContent>
              <p className="text-fg-muted">
                Editorial container caps content at 1280px. 24px gutters mobile, 88px desktop.
                Section vertical rhythm: 80px mobile, 128px desktop.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      <Hairline />

      <section>
        <Eyebrow>04 · Components</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          Primitives.
        </h2>
        <div className="mt-8 space-y-10">
          <div>
            <Eyebrow>Buttons · sentence-case CTAs · hairline borders</Eyebrow>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Button>Primary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
              <Button size="lg">Large</Button>
              <Button disabled>Disabled</Button>
            </div>
          </div>

          <div>
            <Eyebrow>Status pills · muted status colors only</Eyebrow>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <StatusPill tone="neutral">Draft</StatusPill>
              <StatusPill tone="success">Won</StatusPill>
              <StatusPill tone="warning">Stuck</StatusPill>
              <StatusPill tone="danger">Lost</StatusPill>
              <StatusPill tone="info">In review</StatusPill>
            </div>
          </div>

          <div>
            <Eyebrow>Card · hairline border · 14–20px radius</Eyebrow>
            <Card className="mt-4 max-w-md">
              <CardHeader>
                <Eyebrow>Eyebrow · H3 · description</Eyebrow>
                <h3 className="text-xl font-styrene font-bold">Card title.</h3>
              </CardHeader>
              <CardContent>
                <p className="text-fg-muted">
                  Hairline 1px ink at 12% alpha. Rounded 14–20px. Soft warm shadow on hover. Voice
                  is engineer-to-engineer — never breathless.
                </p>
              </CardContent>
            </Card>
          </div>

          <div>
            <Eyebrow>Hairline · 1px · 12% ink alpha</Eyebrow>
            <Hairline className="mt-4" />
          </div>

          <div>
            <Eyebrow>Animated tan link underline</Eyebrow>
            <p className="mt-4">
              Hover the{" "}
              <a href="#" className="link-tan">
                tan link
              </a>{" "}
              — underline scales in over 220ms, cubic-bezier(0.16, 1, 0.3, 1).
            </p>
          </div>
        </div>
      </section>

      <Hairline />

      <section>
        <Eyebrow>05 · Voice</Eyebrow>
        <h2 className="mt-2 text-3xl font-styrene font-bold tracking-tight md:text-4xl">
          Engineer-to-engineer.
        </h2>
        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <p className="text-fg-muted">
            Confident, technical, infrastructure-grade. We speak to engineering leaders and
            developers, not consumers. Sentences are short and declarative. Specifics over hype:
            real numbers, real product names, real compliance acronyms.
          </p>
          <p className="text-fg-muted">
            Pride in open-source. &quot;Proudly Open Source&quot;, &quot;Open by design&quot;,
            &quot;Community Driven&quot; — treated as identity, not a feature bullet. Customer
            testimonials lead with engineering outcomes, not feelings.
          </p>
        </div>
      </section>

      <Hairline />

      <footer className="text-sm text-fg-muted">
        <p>
          Tokens live in <code>packages/ui/src/styles/tokens.css</code>. Adopted verbatim from{" "}
          <code>OffsideLabs-AI/offsidelabs-ai-web/assets/css/tailwind.css</code>. See{" "}
          <Link href="/" className="link-tan">
            home
          </Link>{" "}
          and <code>PLAN.md §9</code>.
        </p>
      </footer>
    </div>
  );
}

function Swatch({
  name,
  hex,
  labelTone,
}: {
  name: string;
  hex: string;
  labelTone: "light" | "dark";
}) {
  return (
    <div className="overflow-hidden rounded-lg border hairline">
      <div className="aspect-square" style={{ background: hex }} aria-hidden />
      <div
        className={`space-y-1 p-3 ${labelTone === "light" ? "bg-ink text-bone" : "bg-bone text-ink"}`}
      >
        <p className="font-mono text-xs">{name}</p>
        <p className="font-mono text-xs opacity-70">{hex}</p>
      </div>
    </div>
  );
}
