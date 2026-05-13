# Claude Code Briefing — Build OffsideLabs.ai

---

## Your Role

You are a **senior staff engineer at a top-tier product company** — Vercel, Linear, Stripe, Anthropic, Figma. You ship marketing sites that other engineers and designers screenshot and reference. Your code is clean, semantic, accessible, performant, and easy for the next engineer to extend. You have strong opinions about design and you push back on lazy, template-feeling work.

You are not a "build me a quick landing page with shadcn defaults" engineer. You are the engineer who is hired specifically because the work has to be distinctive.

---

## Mandatory Setup Before Writing Any Code

1. **Read `/mnt/skills/public/frontend-design/SKILL.md` in full.** This is non-negotiable. Load it, internalize the design tokens, component patterns, and constraints, and treat it as authoritative for this environment.
2. Scan for any other SKILL.md files that look relevant and read them before they become relevant.
3. Before writing the first line of code, generate a **DESIGN.md** that captures: the visual direction you chose, the typography stack and why, the color system, the motion philosophy, and three reference sites whose taste you're aiming at. This is your contract with yourself.

---

## The Mission

Build the marketing website for **OffsideLabs** at **offsidelabs.ai**. This is a brand/holding site for the Offside.AI product suite — four AI-native products under one company. The site must position OffsideLabs as a serious, design-led, AI-native product company that takes craft seriously. It is **not** another OpenAI-wrapper SaaS startup and the site should not look like one.

The deliverable is a **production-quality Next.js application** that could ship tomorrow.

---

## Definition of "Production-Quality"

The bar is unambiguous:

| Dimension | Bar |
|---|---|
| Visual identity | Distinctive on first impression. A designer browsing the web should be able to identify the site's references and respect the choices. |
| Typography | Deliberate type system. No "Inter regular everywhere." Consider Geist, Söhne, GT America, Söhne Mono, or a tasteful serif/sans pairing. Tracking, weights, and scale must be considered, not defaulted. |
| Color | A real palette with intent — not a Tailwind default ramp. Articulate why each color exists. |
| Motion | Used purposefully. Respects `prefers-reduced-motion`. No "everything fades up on scroll" autoplay polish. |
| Accessibility | WCAG AA minimum. Full keyboard navigability. Real focus states, not the browser default outline removed. Color contrast verified. Semantic HTML. ARIA only where necessary. |
| Performance | Homepage LCP < 2s on 4G, JS budget < 200KB to interactive, no layout shift, fonts preloaded with `font-display: swap`, images responsive and modern format. |
| Copy | Concrete, specific, written for a busy founder who has read 50 AI startup landing pages this week. No "revolutionary," "game-changing," "next-generation," "leverage AI to unlock." |
| Code quality | TypeScript strict mode. Component primitives that are well-composed. No util-class soup. Comments where genuinely useful. README that the next engineer can follow. |

---

## What to Avoid (Hard Bans)

- ❌ Generic gradient hero with abstract glow blob behind a one-line headline
- ❌ ✨ sparkle emoji as a substitute for AI being interesting
- ❌ Glassmorphism / frosted glass cards used as decoration
- ❌ "Built for the future" / "Powered by AI" / "Reimagining X" copy
- ❌ Stock 3D Spline shapes, generic Lottie animations, default Framer Motion fade-up cascades
- ❌ Inconsistent design between the four product pages
- ❌ shadcn defaults shipped untouched
- ❌ A pricing table with "Most Popular" highlighted in purple
- ❌ A "Trusted by" logo bar with five fake logos
- ❌ Dark mode that's actually unreadable, picked because "AI sites are dark"

If you find yourself reaching for one of these, stop and produce something better.

---

## The Brand

**OffsideLabs** is the parent brand. **Offside.AI** is the underlying AI infrastructure / model orchestration layer that powers the four products. The name comes from the football (soccer) rule — being beyond the last defender, in a position the defense didn't see coming. The brand voice is **sharp, kinetic, slightly contrarian, technically credible**.

**Lean into that voice subtly** — through typography, motion timing, copy voice, perhaps a single visual motif that nods to it (a line, a moment of asymmetry, a precise geometric reference). **Do not** lean on literal sports imagery. No soccer balls. No field lines. No referee whistles. No "GOAL!" CTAs. The reference is the *idea* of getting ahead of the play, not the *iconography* of football.

**Tone of voice samples to calibrate against:**
- Linear: precise, confident, never explains too much
- Vercel: opinionated, technical, fast-paced
- Anthropic: warm, careful, treats the reader as intelligent
- Stripe: clear, financial-grade, every sentence earns its place

**Tone of voice to avoid:**
- HubSpot blog (over-explained, friendly to the point of unfocused)
- Generic SaaS landing page (vague, hedged, over-promising)
- Y Combinator launch tweet ("the [thing] for [thing]")

---

## The Product Suite

The site must position four products. **Each product page must be substantial, distinctive, and concrete enough that a target buyer can decide whether to book a demo without speaking to anyone.**

### Product 1 — OffsideCRM

**One-line positioning:** The AI-native, vertically configurable CRM. Same core platform; deeply different per industry.

**What it is:** An AI-native CRM with MCP connectors and RAG querying built into the architecture. The same core product is configured into vertical packs (real estate, dental, med spa, personal injury law, fitness, insurance, mortgage, home services) via swappable connector libraries, prompt libraries, and pre-built workflows.

**Why it's interesting (the wedge):** Every major CRM (Salesforce Einstein, HubSpot Breeze, Monday, Zoho) ships the same six AI features to every customer regardless of industry: lead scoring, generative email, conversation intelligence, forecasting, enrichment, chatbots. OffsideCRM ships AI that is *different per vertical* — because the connectors, prompts, and workflows are configurable, not hard-coded.

**Target buyer:** SMB owners and operators in vertical industries that have been forced to bend generic CRMs (Salesforce, HubSpot) to their workflow. Independent real estate agents. Dental practice owners. Med spa operators. Boutique law firms. Pricing range $99–$599/seat/month depending on vertical.

**Headline AI capabilities:** Voice AI receptionist, inbound response agent, follow-up agent, re-engagement agent, RAG-powered "ask your CRM," next-best-action recommender, vertical-specific document generation, audit-logged AI actions with configurable autonomy thresholds.

**Killer differentiators to surface on the page:**
1. MCP connector library (Dentrix, Open Dental, Mindbody, Encompass, Clio, ServiceTitan, MLS, etc.)
2. Vertical packs as a first-class product concept
3. RAG over the customer's own data, not a generic model

---

### Product 2 — OffsideAI-CMS

**One-line positioning:** The content operating system for companies that need to publish like a media team without hiring one.

**What it is:** An AI-native content CMS — built AI-first, not bolted-on. It ingests a company's knowledge base (docs, product specs, customer interviews, support transcripts, internal wikis) and produces:
- SEO-optimized long-form articles on a publishing pipeline
- Brand-voice-tuned social posts scheduled across platforms
- Long-form-to-short-form repurposing (one blog → LinkedIn carousel + Twitter thread + email + YouTube short script)
- Editorial calendar driven by keyword opportunity and brand priorities
- Human-in-the-loop review workflows (so it's not "AI publishes whatever it wants")

**Why it's interesting:** Most "AI content tools" are thin wrappers around GPT that produce generic, ungrounded text. OffsideAI-CMS is grounded in the customer's actual knowledge base via RAG, tuned to their brand voice via fine-tuning or in-context learning, and operates as a *system* (publishing pipeline, calendar, repurposing graph) — not a "generate a blog post" button.

**Target buyer:** Marketing leaders at agencies, SaaS companies, and professional services firms currently spending **$3,000–$8,000/month on content freelancers** for blogs, social posts, and newsletters. The pitch is to make that spend unnecessary while *increasing* output volume and consistency.

**Pricing positioning:** Likely $499–$1,499/month per workspace — priced as a fraction of the freelance spend it replaces.

**The competitive context to acknowledge subtly on the page:** Jasper, Copy.ai, Writer all exist and are well-known. OffsideAI-CMS is differentiated by being a *system* (CMS + pipeline + scheduling + repurposing) rather than a content generator. Don't trash competitors on the page — show, don't tell.

---

### Product 3 — Offside-Agent

**One-line positioning:** Workflow automation for teams who want to read their automations like code, not click them like a flowchart.

**What it is:** An agentic automation platform — a meaningful improvement on n8n / Zapier / Make.com. The differentiator: workflows are defined in a **purpose-built DSL** with **Mermaid syntax for visualization**, so you can write, version, diff, and review automations like code while still seeing them as a diagram.

**Why it's interesting:** n8n and Zapier are point-and-click — which is fine for simple flows but becomes a nightmare at any meaningful complexity. There's no real diff, no real version control, no real code review. Offside-Agent treats workflows as a first-class artifact: text-based DSL → renderable Mermaid diagram → executable graph. Plus it's *agentic* — steps can be AI agents with goals, not just deterministic functions.

**Target buyer:** Engineering-adjacent operators at growing companies — RevOps, growth, customer success, internal tooling teams. The kind of person who hits the limits of Zapier on month two and wishes they could just write the workflow in YAML or TypeScript.

**Headline capabilities to surface:**
1. DSL + Mermaid (the differentiating idea — show this on the page; the page should literally render a Mermaid diagram of an example workflow)
2. AI-native agent steps (a step can be an agent with a goal, not just a function call)
3. MCP connector library (shared with the rest of the OffsideLabs suite)
4. Git-native workflow definitions — diff, review, version

**Competitive context:** n8n, Zapier, Make.com, Workato. Don't name them on the page; differentiate by showing the DSL and the Mermaid output.

---

### Product 4 — OffsideAI-FrontDesk

**One-line positioning:** A voice receptionist that's hired, configured, and live by Friday — not an API you have to assemble.

**What it is:** An AI voice receptionist for SMBs — dental clinics, law firms, real estate offices, accounting practices, vet clinics, med spas. It answers calls, handles natural language, books appointments into the existing calendar, sends confirmation messages, escalates to a human when needed, and logs every interaction.

**The bar:** It must feel indistinguishable from a real receptionist on the phone. If it doesn't, the product fails.

**Competitive context — research these and differentiate clearly:** **Bland AI, Retell AI, and Vapi** are the current market leaders. They are all **infrastructure / API plays aimed at developers**. They sell the building blocks. An SMB dental practice can't actually use them without hiring a developer or an agency.

**OffsideAI-FrontDesk's differentiation lives in three places:**

1. **Vertical-preconfigured turnkey product, not an API.** Pre-trained on vertical-specific FAQs, intake flows, scheduling logic, and tone for dental, legal, real estate, accounting, vet, and med spa. The clinic owner doesn't write prompts. They pick "Dental Practice" and answer ten setup questions.

2. **SMB-friendly pricing.** Flat monthly pricing that's predictable for a small business — *not* per-minute infrastructure pricing that scales unpredictably with call volume. The buyer is a practice manager, not a CTO.

3. **Live integrations on day one.** Native calendar (Google Calendar, Microsoft 365, practice-management software like Dentrix, Open Dental, Clio, ServiceTitan), CRM (OffsideCRM and the major incumbents), and SMS confirmation. The competitors require the customer to wire these up themselves.

**Secondary differentiators worth surfacing:**
- White-glove onboarding (real human helps set up brand voice, scripts, escalation rules)
- Brand-voice mirroring (the receptionist sounds like the practice's actual style, not a generic AI voice)
- Suite integration (calls log to OffsideCRM, transcripts feed OffsideAI-CMS knowledge base, escalations route through Offside-Agent)

**Pricing positioning:** Likely $299–$799/month flat depending on call volume tier. Frame against the cost of a part-time human receptionist (~$2,000–$3,500/month all-in).

**On the product page, do this:**
- Show a real-feeling sample call transcript or audio waveform mockup. Not a stock illustration.
- Show the integration list explicitly with logos.
- Have a section that *acknowledges* the developer-API tools exist and is honest about who FrontDesk is for instead. Confidence reads as honesty.

---

## Site Architecture

Build the following pages. Each must be substantial — no empty stubs.

```
/                          — Homepage
/products/crm              — OffsideCRM product page
/products/cms              — OffsideAI-CMS product page
/products/agent            — Offside-Agent product page
/products/frontdesk        — OffsideAI-FrontDesk product page
/company                   — About OffsideLabs / Offside.AI
/pricing                   — Pricing (decide whether unified or per-product)
/insights                  — Blog/insights index
/insights/[3 sample posts] — Three real, substantive sample articles
/contact                   — Contact / book a demo
```

### Page-Specific Requirements

**Homepage** — must clearly establish:
- The OffsideLabs brand and what unifies the four products (the AI-native architecture, the MCP connector backbone, the vertical configurability)
- The relationship: OffsideLabs (brand) → Offside.AI (engine) → 4 products
- A path into each product
- A non-throwaway "why us" section that earns the visitor's attention

**Each product page** — must include:
- A hero that is *specific* to that product's differentiation, not a templated layout
- A "what makes this different" section that addresses competitors honestly (especially FrontDesk vs. Bland/Retell/Vapi)
- A meaningful demo, mockup, or interactive element appropriate to the product (CRM: pipeline UI mockup; CMS: editorial calendar mockup; Agent: literal Mermaid diagram of an example workflow; FrontDesk: call transcript + integration grid)
- Pricing tier (or pointer to pricing page)
- A specific CTA — different per product based on buyer maturity

**Company page** — substance over fluff. The thesis behind OffsideLabs (why one company is building four AI-native products instead of focusing on one), the team if applicable, the AI infrastructure thesis behind Offside.AI.

**Pricing page** — make the pricing decision deliberately. Per-product seat pricing? Unified workspace pricing? Vertical-specific pricing for CRM? Whichever you choose, justify it in DESIGN.md.

**Insights** — three real sample posts, written with substance. Suggested topics:
1. "Why we believe AI-native CRMs will be vertical, not horizontal" (OffsideCRM thesis)
2. "Workflows as code: why we built a DSL instead of another canvas" (Offside-Agent thesis)
3. "The receptionist test: what 'indistinguishable from a human' actually means for voice AI" (FrontDesk thesis)

These posts establish OffsideLabs as a thinking company. Don't write SEO mush. Write the real argument.

---

## Technical Stack

- **Framework:** Next.js 14+ with App Router, TypeScript strict mode
- **Styling:** Tailwind CSS — but used with restraint. Build component primitives. Don't ship util-class soup.
- **Components:** Build your own primitives. shadcn/ui can be a starting reference but customize aggressively; do not ship default styling.
- **Motion:** Framer Motion (or `motion/react`). Used purposefully. Respect `prefers-reduced-motion`.
- **Mermaid rendering:** Required for the Offside-Agent product page. Use `mermaid` npm package, render client-side.
- **Fonts:** Choose deliberately. Self-host via `next/font`. Do not ship the default Inter regular weight everywhere.
- **Icons:** Lucide is fine, but consider a custom icon set if it strengthens the brand. Generic icons are a tell.
- **Forms:** Server actions + Zod validation. Demo-request form must actually work locally (post to a logging endpoint).
- **Analytics scaffolding:** PostHog or Plausible setup (env-gated, not active by default).
- **Dark mode:** Decide deliberately. If you ship dark mode, treat it as a primary mode with full design consideration. If you don't, default to a thoughtful light mode.

---

## Process

Work through the project in this order. Do not skip steps.

1. **Read `/mnt/skills/public/frontend-design/SKILL.md` in full.**
2. **Generate three distinct visual directions** — describe each in DESIGN.md as 200–300 words covering typography, color, layout philosophy, and reference sites. Pick the strongest and justify the choice.
3. **Build the design system** — `tokens.css`, type scale, color tokens, spacing scale, motion primitives. Commit before building any page.
4. **Build the primitive components** — Button, Link, Card, Section, Container, Heading, Eyebrow, etc. Get these right before you build pages.
5. **Build the homepage.** This sets the visual contract for everything else.
6. **Build the FrontDesk product page next.** It has the clearest competitive differentiation — getting it right validates the design language for the rest of the product pages.
7. **Build the remaining product pages** — CRM, CMS, Agent. Maintain consistency.
8. **Build company, pricing, contact, insights index, and three sample posts.**
9. **Final pass:** Lighthouse audit (target ≥95 across all four scores on the homepage), accessibility audit (axe DevTools clean), copy review (read every sentence aloud — cut anything that sounds like marketing fluff), responsive review (320px → 1920px).

---

## Deliverables

1. Working Next.js application — `npm install && npm run dev` runs cleanly with no warnings.
2. **README.md** — setup instructions, architecture overview, where to find what, how to add a new product page.
3. **DESIGN.md** — the visual direction chosen, why, the type and color system, the motion philosophy, three reference sites.
4. **A clean git history** if you're committing — meaningful commit messages, not "wip" and "fix stuff".

---

## Final Note on Taste

The single biggest failure mode for this project is shipping something that *looks fine* but feels like every other AI startup site on the internet. "Fine" is a failure. The site needs to feel like a place where a strong product team works.

If at any point you find yourself reaching for a layout that you've seen on five other AI sites this month — pause, and produce something better. The brand is called Offside for a reason.

When in doubt, ship less, but make every element on the page deliberate.

Now go build it.