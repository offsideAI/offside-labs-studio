# DEMO.md — OffsideStudio — Agent Marketplace · 5-minute stage demo

> Presenter script for the conference demo. The narrative is **"install one agent → deploy an entire conversion funnel → watch every lead become a paying customer."**

**Selling proposition to lead with:** *"OffsideStudio — Agent Marketplace. One click installs an agent that builds your entire ecommerce funnel — marketing campaign launch, AEO content, ad sync, landing pages, email, cart recovery, payments. Every lead pulled in is a tracked conversion."*

**The hero agent:** 🚀 **Ecommerce Conversion Funnel Optimizer** — a 10-node marketplace agent that choreographs the full lifecycle starting with a marketing-campaign launch. This is the demo headline.

---

## Setup checklist (30 min before demo)

### 1. Terminal — backend up + seeded

```bash
# From repo root:
pnpm backend:up                              # Postgres + Redis + Django web + Celery worker + Beat
pnpm backend:migrate                         # apply all migrations (incl. marketplace 0001 + 0002)
python -m tools.seeds.marketplace            # seeds 15 catalog agents (incl. the hero)
python -m tools.seeds.demo_workspace         # seeds the `acme-demo` workspace + sample CRM
```

Verify:
- `pnpm backend:test apps/marketplace apps/automations` — must be green.
- Visit `http://localhost:8000/admin/marketplace/marketplaceagent/` — should show **15 rows**, with *Ecommerce Conversion Funnel Optimizer* at the top (newest first).
- Visit `http://localhost:8000/admin/workspaces/workspace/` — should show `acme-demo`.

### 2. Frontend — dev server up

```bash
pnpm dev                                     # main surface at :3000
```

Open `http://localhost:3000` in a clean browser profile (no extensions, no autofill).

### 3. Browser pre-state

- Log in as **`demo@offside.ai`** / **`DemoOnly123!`**.
- Land in `/acme-demo` (or whatever the workspace home redirects to).
- **Pre-warm these pages** by clicking each once so they render instantly during the demo:
  - `Agent Marketplace` → `/acme-demo/marketplace`
  - `Agent Design Studio` → `/acme-demo/automations`
  - `Companies` → `/acme-demo/companies`
  - `Deals` (kanban) → `/acme-demo/deals`
- **Open these tabs in this order**, Cmd-1 through Cmd-4 hotkeys:
  1. Agent Marketplace (sitting on the catalog grid)
  2. Companies
  3. Deals
  4. Cmd-K demo (optional)

### 4. Stage-comfort items

- Zoom the browser to **125%** so the audience can read.
- Close devtools.
- Cmd-K **once** to test the palette before going live.
- Have a backup screenshot of the Run Inspector ready in case the live trigger doesn't fire.

---

## The 5-minute narrative

Total budget: **5 minutes** (~5:30 max). The hero agent does most of the lifting — every minute after install is the payoff.

### Step 1 — Frame the product *(0:00 → 0:25)*

**On stage:** Tab 1, sitting on the Agent Marketplace grid.

> "This is OffsideStudio — Agent Marketplace. The pitch is one sentence: install an agent that builds your entire ecommerce conversion funnel. Watch."

- Point at the sidebar — **Agent Marketplace** and **Agent Design Studio** are at the top, **above** Contacts / Companies / Deals. The CRM is the data layer the agents act on.
- Scroll the grid once so the audience sees the variety — 15 agents spanning lead capture, cart recovery, fulfillment, payments, customer service.

### Step 2 — Install the hero agent *(0:25 → 1:30)*

**Click into 🚀 *Ecommerce Conversion Funnel Optimizer*.**

> "One agent. The whole funnel. Marketing campaign launch, AEO content, ad sync, landing pages, email, cart recovery, payments — choreographed end to end."

- The detail page renders the **10-node graph** as a read-only canvas preview. Pan / zoom briefly so the audience can read the node labels.
- Walk the audience through the choreography in one sentence:
  > "It launches the marketing campaign across email + social + search + display, seeds AEO answers, syncs ads, generates landing pages, queues the email welcome, queues the abandoned-cart recovery, queues the payment-success confirmation, and logs a deployment summary on the funnel's CRM record."
- Click **Install to workspace**.
- The page redirects to the Agent Design Studio. Status pill: **active · v1**.

> "One click. The 10-node funnel is now live in my workspace as an editable, published workflow."

**Fallback:** If the install API errors, switch to *Welcome new contact* (simpler graph). Don't troubleshoot live.

### Step 3 — Run it. Live. *(1:30 → 3:00)*

**You're in `/acme-demo/automations/{automation_id}/` with the hero agent open.**

- Walk through the toolbar in one breath: status pill, version pill, save indicator, Describe button, Versions button, Run button, Publish button.
- Click **Run**.
- After ~1–3 seconds the run completes. Scroll down to the **recent runs** footer.
- Click the most recent run row.

**Run Inspector opens. This is the wow moment.**

- Status pill: **completed** (green).
- The metadata grid shows started / finished / current step / **total cost** summed across all 10 step rows.
- Scroll the step-runs list. Each of the 10 nodes has its own card.
- Expand `n2` (Launch marketing campaign) — show `input` (campaign name, channels, budget, target audience), `output` (`status_code`, `headers`, `body`), `cost`, `idempotency_key`. **This is the campaign launch the agent kicked off.**
- Expand `n3` (Seed AEO answer content) — show that `linked_to_campaign_status` was templated from `{{ n2.status_code }}` and resolved to `200`. **Step chaining live.**
- Expand `n6` (Create funnel company record) — show that the action returned a real `company_id`.
- Expand `n7` (Queue email welcome series) — show that `related_id` was templated from `{{ n6.company_id }}` and resolved to the company id we just created.

> "Every step's input, output, cost, and idempotency key is durable. If a worker died mid-funnel, the next attempt would short-circuit on this key — no double side effects."

**Fallback if the run shows `failed`:** Expand the failed step. The error message is in the `error` field. Common culprits: pipeline_id reference (this agent avoids deals, so unlikely) or `ANTHROPIC_API_KEY` (not used by this agent). If unrecoverable, fall back to the backup screenshot.

### Step 4 — Show that it really happened *(3:00 → 4:00)*

**Switch tabs to `/acme-demo/companies`.**

- The new **Acme Demo Funnel** company is at the top of the list. Click it.
- The company detail page shows:
  - **Tasks tab** — three tasks the agent just queued: *Send welcome email*, *Configure abandoned-cart recovery*, *Wire payment-success confirmations*.
  - **Notes tab** — the deployment-summary note with the ✅ checklist of what was deployed.
  - **Activities feed** — `record_created` event from when the agent created the company, plus task/note events.

> "The agent didn't just orchestrate. It built real CRM scaffolding. Tasks the sales team can pick up. A note explaining what was deployed. A company record that's the entry point for every lead that comes through this funnel."

### Step 5 — Customize + bonus *(4:00 → 5:00)*

Time check. If you're ahead of schedule:

**Back to the Agent Design Studio tab.**

- Click the **Describe** button (small AI badge) — the Describe panel slides in.
- Type or paste: *"After payment success, send a thank-you SMS via Twilio."*
- Click **Generate** — Claude streams in a proposed graph. Token + latency + model name visible.
- Click **Discard** (we don't want to overwrite the hero).
- Close the Describe panel.

> "And every agent you install — or describe to Claude in English — is editable in the Design Studio. Versioned. Inspectable. Real."

**Closing line:**
> "One click installs your conversion funnel. The Marketplace has 14 more agents for specific lifecycle stages. Or design your own. OffsideStudio — Agent Marketplace. Thanks."

**Fallback for time:** Skip step 5 entirely if you're at 4:30. The Step 4 reveal is the second wow.

---

## Time-pacing tips

- **The 10-node Run Inspector is the wow moment.** Don't rush expanding the step rows — give the audience 2–3 seconds per expand to read the input/output JSON. Focus on n2 (campaign launch), n3 (AEO with templated `linked_to_campaign_status`), and n6/n7 (real company + templated task linkage).
- **The Step 4 reveal lands the "it really happened" message.** Audiences with sales/CRM backgrounds will instinctively pattern-match company + tasks + notes as evidence the agent did real work, not just printed logs.
- **If something breaks at step 3:** stay calm, fall back to the screenshot, narrate it as "this is what it looked like in rehearsal — exact same graph, exact same Inspector view." The audience won't know.
- **Don't apologize for placeholders.** The httpbin URLs on n2/n3/n4/n5 are intentional — they prove the HTTP call mechanics work + leave a real shape the user fills in for their actual campaign orchestrator, AEO platform, ad provider, landing-page tool. Frame as: "swap each of these for your real integration."

---

## Common issues + quick fixes

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Marketplace grid empty | Seed not run | `python -m tools.seeds.marketplace` in another terminal |
| Hero agent missing | Seed run before the hero was added | Re-run `python -m tools.seeds.marketplace` (idempotent) |
| Login fails | EmailAddress row missing | Re-run `python -m tools.seeds.demo_workspace` |
| Install returns 401 | Workspace context not loaded | Refresh the page after login |
| Install returns 409 | Hero agent `is_published=False` | Edit in Django admin to flip back to True |
| Run shows `failed` | An action raised | Expand the failed step — `error` field shows the cause; most likely network if httpbin is unreachable |
| Recent run doesn't appear in footer | Celery worker is down | Verify `docker compose ps` — worker should be `Up` |
| `n6.related_id` resolves to `null` | `n5` didn't run (or didn't return `company_id`) | Re-run; if persistent, check n5's output in the Inspector |
| Describe panel hangs | `ANTHROPIC_API_KEY` missing | Skip Step 5; close the panel and finish on Step 4's wow |

---

## Pre-stage hash check

Run before going on stage:

```bash
# 15 marketplace agents seeded (including the hero)
docker compose -f backend/docker-compose.yml exec web \
    python manage.py shell -c "from apps.marketplace.models import MarketplaceAgent; \
        print('agents:', MarketplaceAgent.objects.count(), \
        'hero:', MarketplaceAgent.objects.filter(slug='ecommerce-conversion-funnel-optimizer').exists())"
# → agents: 15 hero: True

# demo workspace exists with sample data
docker compose -f backend/docker-compose.yml exec web \
    python manage.py shell -c "from apps.workspaces.models import Workspace; \
        from apps.contacts.models import Contact; \
        from apps.companies.models import Company; \
        ws = Workspace.objects.get(slug='acme-demo'); \
        print('contacts:', Contact.objects.filter(workspace=ws).count(), \
        'companies:', Company.objects.filter(workspace=ws).count())"
# → contacts: 20 companies: 8

# demo user JWT works
curl -X POST http://localhost:8000/api/auth/login/ \
    -H 'Content-Type: application/json' \
    -d '{"email":"demo@offside.ai","password":"DemoOnly123!"}' | jq -r .access | head -c 30
# → "eyJ0eXAiOi..."
```

All three pass → green for stage.

---

## The narrative arc, condensed

For when you need to remember the spine of the demo at 30,000 feet:

```
Frame    → Marketplace + Studio above the CRM. (25s)
Install  → 🚀 Funnel Optimizer · 10 nodes · one click. (65s)
Run      → Click Run. 10 step rows. Campaign → AEO → ads → ... (90s)
Reveal   → Switch to Companies. Real records. Real tasks. (60s)
Custom   → Describe in English. Bonus. (60s)
Close    → "One click installs your conversion funnel." (10s)
```

---

*Last revised: 2026-05. Aligned with PRD.md v3.1+ and ROADMAP.md Revision 14.*
