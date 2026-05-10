# Offside CRM — PLAN.md

> First product in the Offside Studio Suite. AI-native CRM with deeply integrated workflow automation. This document is the single source of truth for what we are building, how, and in what order.

**Status:** Pre-build. Captures interview decisions (Rounds 1–7) and locks the architectural bets for the suite.
**Owner:** Offside Labs.
**Last revised:** 2026-05 (revision 2 — DO App Platform deployment, Celery-based workflow engine, flatter monorepo).

---

## 1. Executive summary

We are building **Offside CRM**, the first of four products in the Offside Studio Suite (CRM, Crunch, Design, Director). It is positioned for **SMB sales teams (2–20 reps)** as a complete CRM that fuses a polished record/pipeline experience (HubSpot/Attio lineage) with a workflow automation engine (Zapier/n8n lineage) and pervasive AI. The wedge is **"AI everywhere"** — prompt-first authoring, conversational data access, and agentic-when-allowed action.

Each product in the suite shares: design system, auth, AI infra, workflow primitives, API client. Cross-cutting concerns live in `packages/*` from day one so Crunch / Design / Director don't have to be re-platformed later, even though the suite-app placeholders themselves are deferred under the flatter monorepo shape (§11, §14).

Stack: **Next.js 15 (Vercel)** for the web frontend, **Django + DRF (Digital Ocean App Platform)** for the backend, **SwiftUI** for iOS, **Celery + Redis** for durable workflow execution with a thin custom Django layer for graph walking and HITL, **pgvector** for semantic search, **Claude (default) + OpenAI/Gemini fallback** for AI, **allauth + dj-rest-auth + SimpleJWT** for auth, and **OpenAPI codegen** as the type contract between frontends and backend.

The MVP cut is intentionally **ambitious**: full Round-1–3 scope shipped over ~14–17 sequential milestones, each with a working demo. No AI feature is silent; no workflow loses state on restart; no UI surface ships without keyboard navigation, focus management, and a11y.

---

## 2. Product vision & positioning

> "Make HubSpot's CRM core, Zapier's automation flexibility, and Attio's design polish feel old."

Operating principles (from the brief, locked):
- **AI-native, not AI-adjacent** — every record view, automation, search, and follow-up is AI-aware. AI drafts, classifies, routes, and (where allowed) acts.
- **Automation as a peer, not a side panel** — workflows and CRM records share one mental model, one schema language, one event bus.
- **Web-first** — modern stack, sub-100ms feel. Native iOS is a *peer* surface (Round 6 override), not a port.
- **Opinionated UX** — keyboard-first, command palette, dense-but-calm.
- **The 80–90% of Zapier** — most-used capabilities with a dramatically better authoring experience, especially around AI steps.

Suite positioning: each product solves a different surface, but they share a coherent voice and visual system. Offside is engineer-to-engineer, confident, never breathless.

---

## 3. Target user & wedge

**Primary user:** SMB sales teams, 2–20 reps. Manager + IC personas matter equally — the manager configures pipelines and automations, the IC lives in records and inbox.

**Wedge — "AI everywhere":**
1. **Prompt-first workflow authoring** — users describe a workflow in English; Claude generates the node graph; user edits visually. (User selected pure node graph as the canvas; AI authoring sits on top.)
2. **Conversational data layer** — natural-language queries return structured results plus suggested follow-ups. ("Show deals over $10k that went quiet last week.")
3. **Comms intelligence** — drafts, reply suggestions, thread + meeting summaries, follow-up nudges in every record view.

We are not building "the most integrations." We are building "the best authoring experience for AI-native automations" with enough integrations to cover 80–90% of common SMB sales workflows on day one.

---

## 4. MVP scope

User selected **AMBITIOUS** in Round 6: full Round-1–3 scope. Below is what that means concretely. Phasing — not de-scoping — is how we reconcile this with realism.

### 4.1 Entities (data model surface)
- **Workspaces / Memberships / Roles** — multi-tenant from day one. Roles: owner, admin, manager, rep, read-only.
- **Contacts** — fixed core: first/last name, primary email, phone(s), title, company FK, owner FK, source, lifecycle stage, created/updated. Plus **custom fields** (workspace-defined).
- **Companies** — fixed core: name, domain, size band, industry, owner FK. Plus custom fields.
- **Deals** — fixed core: name, value, currency, stage (configurable per pipeline), pipeline FK, owner FK, expected close, contact + company FKs. Plus custom fields.
- **Tasks** — fixed core: title, due, owner, related record (polymorphic), status, priority. Plus custom fields.
- **Notes** — body (Markdown), related record (polymorphic), author, created.
- **Activities** — append-only event log: emails sent/received, calls, meetings, AI actions, automation runs, field changes.
- **Pipelines** — workspace-defined deal stages.
- **Custom field definitions** — per workspace, per entity type. Types in v1: `text`, `long_text`, `number`, `select`, `multi_select`, `date`, `datetime`, `boolean`, `url`, `email`, `phone`, `relation`. Formula and lookup deferred.
- **Email threads + messages** — synced from Gmail.
- **Calendar events** — synced from Google Calendar.
- **Automations** — triggers, action graphs, runs, run steps. Owned and executed entirely in Django (§7).
- **Agent policies** — workspace-level action-mode table (per action type: `suggest` | `approve` | `autonomous`).
- **Embeddings** — pgvector store keyed to source records (notes, emails, deal/contact summaries).

### 4.2 Triggers (Round 2 — all in)
- Record events: `created`, `updated`, `field_changed`, `deleted`.
- Time: schedule (cron), `delay_until`, `every_n` (recurring).
- External: webhook (inbound), form submission, **email received** (Gmail push via Pub/Sub; polling fallback).
- AI conditions: classifier-on-event ("when sentiment turns negative", "when intent detected").

### 4.3 Actions (Round 2 — all in)
- CRM mutations: create/update/delete record; assign owner; move pipeline stage; add tag.
- Communication: send Gmail (as connected user); post to Slack channel/DM; in-app notification.
- Logic: branch (if/elif/else), delay, loop over list, **human-in-the-loop approval** (custom durable pause; signed approval link).
- AI: prompt Claude (with model picker), classify, extract structured data (Pydantic schema), draft text, summarize.
- HTTP: outbound HTTP request with auth presets.

### 4.4 Integrations (Round 2 — all in)
- Google: **Gmail** (read, send, push) + **Google Calendar** (read, write).
- **Slack** — channel + DM notifications, single-workspace OAuth.
- **CSV** import + **HubSpot / Pipedrive** import (CRM-to-CRM mappings; this is the switching-cost killer).
- **Generic webhook** (in) + **HTTP request** (out).

### 4.5 AI capabilities (Round 3 — all in)
- Email & comms: drafts, reply suggestions, thread + meeting summaries, follow-up nudges. Surface: every contact + deal view.
- NL data layer: NL → structured query (filter + sort + groupBy). Surface: global cmd-K and saved views.
- Lead scoring + enrichment: background AI populates company size, role, intent signals on new contacts/companies. Cost-guarded.
- Suggested next actions: per-record AI suggestion strip. Calm, never chatbot-y.

### 4.6 Agent autonomy (Round 3 — selected)
- Policy: **default-suggest, opt-in autonomous per action type**. Per-workspace action-mode table.
- HITL surface: in-app inbox + email magic-link approval + iOS push notification with action buttons.
- Audit: every agentic action logged with prompt, model, cost, output, and post-hoc undo where reversible.

### 4.7 Surfaces
- **Web:** responsive Next.js 15 app, light-first per brand book, compact density, keyboard-first.
- **iOS:** native SwiftUI client, MVP day-one, scope = full CRM client (browse/edit contacts/deals, run workflows, approve agentic actions, push notifications).
- **Mobile web:** responsive web fallback so Android/desktop browser users aren't blocked.

### 4.8 Phasing note
"AMBITIOUS day-one" doesn't mean every feature ships in milestone 1. It means we don't *cut* features — we sequence them across ~14–17 milestones (one extra vs. the Inngest plan, because rolling our own durable graph walker on Celery adds work). Every milestone produces a working demo. Section 13 is the milestone plan. If you decide partway through to ship sooner, we can "pull the cord" at any milestone and the result is releasable.

---

## 5. Tech stack

| Concern | Choice | Notes |
|---|---|---|
| Web framework | **Next.js 15** (App Router, RSC) + TypeScript strict | No `any`. Deployed to **Vercel**. |
| Backend framework | **Django 4.2 LTS + DRF** | Fresh project; SaucyCart referenced for patterns only. Deployed to **Digital Ocean App Platform** (web component + worker components). |
| Auth | **django-allauth + dj-rest-auth + djangorestframework-simplejwt** | Custom user (email-based). Web + iOS consume JWT (access 1d / refresh 14d, blacklist on logout). |
| API contract | **OpenAPI 3.1 from `drf-spectacular`** → `openapi-typescript` (web) + Swift codegen (iOS) | CI fails on schema drift. |
| Database | **Postgres 16 + pgvector** | DO Managed Postgres (or Neon if we ever migrate; DO is the default). |
| ORM | Django ORM | Drizzle dropped — type chain runs through OpenAPI. |
| Task queue / scheduler | **Celery 5 + Redis** (DO Managed Redis as broker + result backend; Celery Beat for crons) | Replaces Inngest. See §7 for the durable-workflow layer we build on top. |
| Workflow durable runtime | **Custom Django layer on Celery + Postgres** (`Automation`, `AutomationRun`, `AutomationStepRun`, `HitlRequest`, "run advancer" Celery task) | All durable state in Postgres. Redis is purely message transport. See §7. |
| Workflow canvas | **React Flow (xyflow)** | Pure node-graph (Round 2). MIT licensed. |
| AI | **Anthropic SDK (Claude 4.7 Opus / Sonnet 4.6 / Haiku 4.5)** + thin model-router over **OpenAI** + **Google Gemini** | Default Claude per task; provider fallback for cost/outage. |
| Vector store | **pgvector** in the same Postgres | Embeddings on notes, emails, deal/contact summaries. |
| Web UI | **Tailwind CSS** + **shadcn/ui** keyed to Offside brand tokens | `tailwind.css` from `OffsideLabs-AI/offsidelabs-ai-web` adopted as our token contract. |
| iOS | **SwiftUI** (iOS 17+), Swift Package Manager, OpenAPI-generated client | Push: APNs via Django backend on DO. |
| Auth on mobile | JWT bearer in Keychain | Refresh-on-401 interceptor. |
| Hosting | **Vercel** (web) + **DO App Platform** (Django web + Celery worker + Celery Beat) + **DO Managed Postgres** + **DO Managed Redis** | Single-cloud-ish. Mirrors SaucyCart's posture: gunicorn web service, worker components, env-var-driven settings. |
| Observability | Sentry (web + iOS + Django + Celery), PostHog (analytics), structured logs, **Flower** (optional Celery operational view) | Custom "Run inspector" UI in Django admin shows workflow runs / steps / cost / latency. |
| Monorepo | **pnpm workspaces** (Turborepo optional) | Flatter shape per user revision (§11). |
| CI | GitHub Actions | Lint, type-check, OpenAPI codegen drift check, Django tests, web tests, iOS build (best-effort). |

### 5.1 Stack contradictions resolved during the interview
| Brief / earlier round said | Reality / new decision | Resolution |
|---|---|---|
| Drizzle ORM, tRPC | Hybrid Next.js + Django backend | **Dropped Drizzle + tRPC.** OpenAPI codegen replaces both for type-safety. |
| Django allauth + dj-rest-auth (Round 4) vs SaucyCart's Djoser+SimpleJWT | User chose allauth + dj-rest-auth | **Going with allauth + dj-rest-auth + SimpleJWT.** No SaucyCart auth-code reuse. |
| DRF (Round 4) vs SaucyCart's Ninja | User chose DRF | **DRF.** drf-spectacular for OpenAPI. |
| Round 5 dark-first violet/blue | Brand book is light-first tan | **Brand book wins** (§9). |
| Round 5 Inter/Geist | Brand book is Styrene A → Roboto → JetBrains Mono | **Brand book wins.** |
| Native iOS not in brief | User added in Round 3 | **Native iOS day-one.** `frontend-ios/`. |
| Inngest as orchestrator (Rounds 4+6) | User asked to replace with DO-deployable substitute | **Celery + Redis + custom Django durable layer** (§7). |
| Hosting candidates Render/Fly.io | User chose DO App Platform | **DO App Platform** for backend; Vercel for web. |
| `apps/` + `packages/` Turborepo layout | User asked for flat `frontend-web/` + `backend/` | **Flat layout** with `packages/` for shared TS code (§11). |

---

## 6. Data model

This is the **logical** model; physical migrations come at scaffold time. All tables are workspace-scoped via `workspace_id` (indexed). Custom fields use a JSONB column on each entity plus a definition table.

```
workspace (id, name, slug, plan, created_by_user_id, created_at)
membership (id, workspace_id, user_id, role, invited_at, joined_at)
user (id, email[unique], full_name, avatar_url, ... allauth/SimpleJWT fields)

contact (id, workspace_id, first_name, last_name, primary_email, phones[], title,
         company_id, owner_id, lifecycle_stage, source, custom JSONB,
         created_at, updated_at)
company (id, workspace_id, name, domain, size_band, industry, owner_id, custom JSONB, ...)
deal    (id, workspace_id, name, value_cents, currency, pipeline_id, stage_id,
         owner_id, expected_close, contact_id, company_id, custom JSONB, ...)
task    (id, workspace_id, title, due_at, owner_id, related_type, related_id,
         status, priority, custom JSONB, ...)
note    (id, workspace_id, body_md, related_type, related_id, author_id, created_at)

pipeline           (id, workspace_id, name, stages JSONB[ordered])
custom_field_def   (id, workspace_id, entity_type, key, label, type, options JSONB,
                    required, indexed, created_at)
saved_view         (id, workspace_id, entity_type, name, filter_dsl JSONB, sort JSONB,
                    columns JSONB[], owner_id)

email_thread   (id, workspace_id, gmail_thread_id, subject, last_message_at,
                contact_ids[], deal_id?, ...)
email_message  (id, thread_id, gmail_message_id, from_email, to_emails[], html, text,
                sent_at, direction)
calendar_event (id, workspace_id, gcal_event_id, summary, start, end, attendees[],
                related_records[], ...)

activity (id, workspace_id, kind, actor_user_id?, actor_kind, related_type,
          related_id, payload JSONB, occurred_at)
   -- kind: email_sent, email_received, call_logged, meeting_held, ai_action,
   --       automation_run, field_changed, ...

automation              (id, workspace_id, name, status, trigger JSONB, graph JSONB,
                         version, created_by, created_at)
automation_run          (id, automation_id, workspace_id, status, trigger_payload JSONB,
                         current_step_id, state_snapshot JSONB, attempt,
                         resume_at TIMESTAMP NULL, awaiting_event_key TEXT NULL,
                         started_at, finished_at, advancer_task_id TEXT NULL)
   -- status: pending | running | awaiting_approval | awaiting_delay | awaiting_event
   --        | completed | failed | cancelled
automation_step_run     (id, run_id, step_id, attempt, status, started_at, finished_at,
                         input JSONB, output JSONB, model, cost_cents, error JSONB,
                         idempotency_key UNIQUE)
   -- (run_id, step_id, attempt) is the idempotency key; action endpoints look this up
   -- before performing side effects.
agent_policy            (id, workspace_id, action_type, mode)
   -- mode: suggest | approve | autonomous
hitl_request            (id, run_id, step_id, summary, payload JSONB,
                         expires_at, decided_at, decided_by, decision)

embedding (id, workspace_id, source_type, source_id, embedding vector(1536), text,
           model, created_at)
   -- INDEX hnsw (embedding vector_cosine_ops)

integration_connection (id, workspace_id, provider, external_account_id, scopes JSONB,
                        tokens JSONB[encrypted], status)
```

Decisions and notes:
- Custom fields = JSONB column + per-workspace definitions. We don't add columns dynamically. Indexable via expression indexes on hot fields only.
- Polymorphic `related_type` + `related_id` for tasks / notes / activities. Avoiding GenericForeignKey's perf cost — using a small enum + ID.
- All mutating actions emit an `activity` row + a Celery event (workflow advancer enqueue or signal handler).
- Vector embeddings are written async by Celery tasks on entity create/update.
- Soft-delete via `deleted_at` on entities that workspaces care about (contacts, deals). Hard-delete on activities/runs.
- **Durability:** every state change to `automation_run` is a single Postgres transaction that also writes the `automation_step_run` outcome (and optionally re-enqueues the advancer Celery task). Crash-safe — on worker restart, Celery resends in-flight tasks; idempotency-key checks short-circuit duplicates.

---

## 7. Automation engine architecture (revised — Celery + custom Django durable layer)

### 7.1 Topology
```
[Trigger source]                                 [Django emits]                  [Celery]
─────────────────────────────────                ───────────────                 ────────────
Django ORM signal (record_*)                  →  trigger_match → enqueue advancer  → run_advancer task
Inbound webhook endpoint (Django)             →  trigger_match → enqueue advancer
Celery Beat periodic task (cron schedules)    →  enqueue advancer for matching automations
Celery Beat "wake-up sweep" (every 1 min)     →  finds runs with resume_at <= now → enqueue advancer
Gmail Pub/Sub push → /gmail/push (Django)     →  trigger_match → enqueue advancer
HITL approval API (POST /hitl/<token>/decide) →  flip run status → enqueue advancer

run_advancer(run_id):
  1. SELECT FOR UPDATE the run row.
  2. If status not running, exit.
  3. Determine next step from graph + current_step_id + state_snapshot.
  4. Resolve step kind:
       - mutation/comms/HTTP/AI: call action handler with idempotency key
                                  (run_id, step_id, attempt). Persist step result.
       - branch: evaluate condition against state, advance.
       - delay: set status = awaiting_delay, resume_at = now + duration. Exit.
       - approval: create HitlRequest row, set status = awaiting_approval. Exit.
       - wait_for_event: set status = awaiting_event, awaiting_event_key. Exit.
       - loop: persist iterator state, run body for first/next item.
       - end: set status = completed.
  5. Update run_state in same transaction; if running, re-enqueue advancer.
```
- **Source of truth = Django + Postgres.** Celery is the *executor message bus*, not the durable store.
- **Each step is idempotent** by `(run_id, step_id, attempt)`. Action handlers check for an existing `automation_step_run` with the same key and return its cached output.
- **HITL pauses** are durable: the run sits at `awaiting_approval` until the approval API endpoint flips it. Approval token is JWT-signed (action_token-style) so the user clicks a magic link from email or taps "Approve" on iOS push to mutate state without auth login.
- **Delays / waits** are picked up by the Beat "wake-up sweep" (every 1 min) which finds runs where `resume_at <= now()` or `awaiting_event_key` matches a fresh event and enqueues advancers for them. (60-second jitter is acceptable for sales-CRM-grade workflows; we can tighten later.)
- **Cost & latency surfaced** per step: model, tokens, cost, duration in `automation_step_run`. Visible in run-detail UI.

### 7.2 Authoring UX
- Pure node graph (React Flow), nodes for triggers / conditions / actions / AI / loops / waits / approvals.
- "Describe in English" panel (Round 2 add-on): user types intent, Claude returns a node graph as JSON, canvas hydrates.
- Versioning: every save is a new `automation.version`; runs reference the version that started them.

### 7.3 Trigger ingestion
- **Record events:** Django `post_save`/`post_delete` signals + a denormalized "diff" → trigger-match query → enqueue advancer for each matching automation.
- **Time:** Celery Beat — periodic task per automation with a schedule trigger; also the every-1-min wake-up sweep for delays/waits.
- **Webhook:** Django endpoint with per-workspace HMAC; trigger-match → enqueue advancer.
- **Form submission:** Django form endpoint; same path.
- **Email received:** Gmail Pub/Sub → Django `/gmail/push` → ingest message → trigger-match.
- **AI condition:** evaluated as the *first node* of the graph, not a separate trigger primitive — the run starts on the broader event, the AI step decides whether to continue.

### 7.4 Why not pure Celery (and what we add)
Celery alone gives us tasks + retries + scheduling. It does not give us:
- Durable workflow graph state across many short-lived steps (we add `AutomationRun.state_snapshot`).
- HITL pause/resume (we add the row-status flip + signed approval API).
- Run inspection UI (we add a Django admin "Run inspector" view).

That custom layer is ~1.5 milestones of work. It's the cost of dropping Inngest. It's well-understood territory.

### 7.5 Alternatives we kept on the shelf
- **Hatchet** (open-source, Postgres-backed, self-hostable) — Inngest-class features. Adds another DO component. Worth re-evaluating if our custom layer's complexity grows (see §14).
- **DBOS** (Postgres-only durable Python execution) — lower custom-code volume; younger ecosystem. Worth a spike post-MVP.
- **Temporal** — too heavy for MVP ops.

---

## 8. AI architecture

### 8.1 The `packages/ai` package
- **Model router**: dispatch by task → `claude-haiku-4-5-20251001` (classify, extract small), `claude-sonnet-4-6` (draft, summarize), `claude-opus-4-7` (multi-step reasoning, agent planning). Fallback chain to OpenAI / Gemini on outage or cost spike.
- **Structured outputs**: every prompt has a Zod (TS) and Pydantic (Py) schema. JSON-mode + retry-with-correction loop, max 2 retries.
- **Prompt registry**: every prompt is named + versioned (e.g., `comms.draft_reply.v3`). Lives in code, not DB.
- **Telemetry hook**: every call emits `{ prompt_name, model, tokens_in, tokens_out, cost_cents, latency_ms, run_id?, step_id? }`. Visible in Django admin and per-run UI.
- **Caching**: Anthropic prompt caching for system prompts and large reference docs. Hash-keyed in-process LRU for idempotent NL→query results.

> Note: the AI router exists in two parallel surfaces — TypeScript in `packages/ai` for web/iOS-bound AI calls (NL data layer, drafts), and a Python equivalent inside `backend/offside_ai/` for server-side AI calls (classify, enrichment, agent planning, AI workflow steps). Same prompt registry, dual-language helpers. See §11.

### 8.2 NL data layer
- Pipeline: **NL → schema-aware Claude → structured `filter_dsl` JSON** → server-side query → results + summary.
- Schema injected into the prompt: entity types, field names, custom fields, allowed operators. Cached per workspace per schema version.
- Embeddings used only when keyword filters fail or query is fuzzy ("deals that smelled risky"). Hybrid keyword-then-vector-rerank.

### 8.3 Lead scoring + enrichment
- Celery task on `signals.contact_created` / `signals.company_created`.
- Steps: 1) extract domain → search → enrichment Claude prompt → fill structured fields. 2) score Claude prompt → write `lead_score` custom field.
- Cost guardrail: per-workspace daily token budget; over budget → enqueue and notify owner.

### 8.4 Comms intelligence
- Draft on demand from contact/deal view. Streaming. User can edit before send.
- Thread summary on Gmail thread open (cached per latest `last_message_at`).
- Meeting summary triggered post-event by GCal hook + (eventually) call recording integration. v1 = manual paste of transcript or notes.

### 8.5 Agentic loop (Round 3 selection)
- Surface: per-deal/per-contact "Agent assist" toggle. Workspace policy decides which actions need approval.
- Loop: plan → propose actions → for each action check policy → if `autonomous` execute, if `approve` open HITL, if `suggest` add to inbox. Cap at N steps per session.
- Every action logged in `activity` with reversibility status. Reversible actions get a 60-second undo affordance in the UI.
- Implementation: a long-running automation graph with an "agent step" node that loops until done or capped. The HITL primitive is reused.

---

## 9. Brand & design system

### 9.1 Authoritative source
The OffsideAI Design System v1.0 (April 2026 brand book) + the production CSS at `OffsideLabs-AI/offsidelabs-ai-web/assets/css/tailwind.css` are the source of truth. We **adopt the production CSS verbatim** as the starting point of `packages/ui` and extend it with shadcn-keyed component primitives.

### 9.2 Color tokens (locked)
```
--brand-tan:       #C9A389   (accent — the only saturated brand color)
--brand-tan-text:  #7A5F44   (WCAG-safe tan-on-bone for body copy)
--brand-ink:       #1E1E1E   (text on light, surface on dark)
--brand-bone:      #F1F1F1   (primary surface, light-first)
--brand-rule:      rgba(30,30,30,0.12)   (hairline, light)
                   rgba(241,241,241,0.14) (hairline, dark)
--brand-muted:     rgba(30,30,30,0.64)   (muted text, light)
                   rgba(241,241,241,0.72) (muted text, dark)
```
Forbidden: saturated blue, purple, magenta, cyan. Photography uses `.warm-grade` (`saturate(0.7) sepia(0.08)`).

### 9.3 Mode
- **Light-first.** Default surface is bone. Dark surface (`[data-theme="dark"]`) is **scoped per section** (code panels, terminals, hero blocks, footer) — not a global toggle.
- A user-level "Dark UI" preference is *deferred*; we ship light-only chrome with dark code/terminal blocks.

### 9.4 Typography
```
--font-styrene: "Styrene A", "Söhne", "Inter", ui-sans-serif, system-ui, sans-serif
body:    Roboto (Open Font License)
mono:    JetBrains Mono
```
- Display = Styrene A (paid, Commercial Type) → falls through Söhne → Inter → system. We ship without Styrene A licensed; it activates the moment the woff2 files are dropped in `frontend-web/public/fonts/`.
- Type roles (from the brand types file): `display-xl`, `display-l`, `h2`, `h3`, `eyebrow`, `lead`, `body`, `caption`, `code`.
- Eyebrows: UPPERCASE, 0.18em tracked, Styrene 700, tan-text color.
- Section headers: sentence case, end with a period (e.g., "Open by design.").
- CTAs: sentence case. Never ALL CAPS.

### 9.5 Spacing & surface
- Base unit: **4px**.
- Six radius steps: 2 / 4 / 8 / 12 / 16 / pill. Cards 14–20px.
- Four shadow elevations, soft warm-neutral. **Never dramatic.**
- Editorial container: 1280px max, 24px gutters mobile, 88px gutters desktop.
- Section vertical rhythm: 80px mobile, 128px desktop.

### 9.6 Components (carryover from brand book)
- Buttons: sentence-case CTAs, hairline borders, soft shadows.
- Cards: hairline border, eyebrow + H3 + description, 14–20px radius.
- Nav: sticky, 80% bone, 12px backdrop blur.
- Status pills: muted status colors only (no neon). Display-weight metrics.
- Code panel: dark `#161616`, tan-keyed syntax.
- Live feed / ticker: 2.5s on REALTIME.
- Hairline rules: 1px ink at 12% alpha (light) / bone at 14% alpha (dark).
- Animated tan link underline: 220ms `cubic-bezier(0.16, 1, 0.3, 1)`.

### 9.7 Iconography
- **Lucide**, 1.5–2px stroke, MIT. Custom marks dropped into `packages/ui/src/icons/` as needed.

### 9.8 Voice & tone
- Engineer-to-engineer. Confident. Specifics over hype. Real numbers, real names.
- Customer testimonials lead with engineering outcomes, not feelings.
- Pride in open-source.
- Motion: page transition 200ms fade + 8px translate. Reduced-motion contract collapses to 0.001ms.

### 9.9 Accessibility (locked from production CSS + brief)
- Focus-visible: 2px tan outline, 2px offset, 1px radius.
- WCAG 2.2 AA contrast respected (the `--brand-tan-text` adjustment from spec was made for this reason — keep the fix).
- All keyboard nav from day one. Cmd-K palette, j/k row nav, slash search, esc to close.
- Skip-link wired into web app shell.

---

## 10. Suite identity & per-product hues

The suite shares wordmark + OA monogram + tan accent. Each product gets a **secondary warm hue** (a tan-derivative) used sparingly for product-specific UI accents (sidebar tab, app icon dot). All hues are warm-neutral derivatives — never saturated blue/purple/cyan.

| Product | Letter | Secondary hue (proposal) | Rationale |
|---|---|---|---|
| Offside CRM | **C** | `#C98F89` (warm clay / muted coral) | Relationships, comms — slight pink-warm tilt. |
| Offside Crunch | **X** (per user, X for "spreadsheet") | `#D9BCA4` (warm wheat) | Data, calm — lighter tan derivative. |
| Offside Design | **D** | `#A07857` (umber) | Creative, grounded — deeper warm. |
| Offside Director | **R** | `#7A5F44` (deep tan, same as `--brand-tan-text`) | Marketing, gravitas — anchored in the readable tan. |

These are proposals to refine. They satisfy the "no saturated colors" rule and live as `--product-secondary` per app shell.

Suite favicon: the OA monogram (two overlapping tan circles, 3px stroke) — already shipped at `OffsideLabs-AI/offsidelabs-ai-web/public/favicon.svg`. Per-app favicons append the product letter to the right of the monogram.

---

## 11. Monorepo structure (revised — flat)

User chose a flat layout. CRM is the focus; the other suite apps' placeholders are deferred (§14). Shared packages still sit at the suite shape so adding Crunch / Design / Director later doesn't refactor them.

```
offside-labs-studio/                        # this repo
├─ frontend-web/                            # Next.js 15 App Router (deploys to Vercel)
│  ├─ app/
│  ├─ public/
│  ├─ vercel.json
│  └─ package.json
├─ backend/                                 # Django + DRF + Celery (deploys to DO App Platform)
│  ├─ offside_crm/                          # Django project (settings, urls, asgi/wsgi)
│  ├─ apps/                                 # Django apps (workspaces, contacts, deals, ...)
│  │  ├─ workspaces/
│  │  ├─ contacts/
│  │  ├─ companies/
│  │  ├─ deals/
│  │  ├─ tasks/
│  │  ├─ notes/
│  │  ├─ activities/
│  │  ├─ pipelines/
│  │  ├─ integrations/                     # Gmail, GCal, Slack OAuth + sync
│  │  ├─ automations/                      # Automation, AutomationRun, advancer task, HITL
│  │  ├─ agents/                           # Agent policy, agent loop
│  │  └─ ai/                               # Python AI router, prompt registry, telemetry
│  ├─ requirements.txt
│  ├─ pyproject.toml
│  ├─ Procfile                             # web + worker + beat (DO App Platform)
│  ├─ Dockerfile                           # for local + DO build
│  ├─ docker-compose.yml                   # local dev: postgres + redis + django + worker + beat
│  └─ .env.sample
├─ frontend-ios/                            # SwiftUI Xcode project (out-of-Node, generated via xcodegen)
│  ├─ Project.yml                          # xcodegen spec
│  ├─ OffsideCRM/                          # app sources
│  └─ Generated/                           # OpenAPI Swift client (generated, gitignored)
├─ crunch-web/                              # Suite placeholder (Next.js, 10-line shell)
├─ design-web/                              # Suite placeholder (Next.js, 10-line shell)
├─ director-web/                            # Suite placeholder (Next.js, 10-line shell)
├─ packages/                                # shared TypeScript code
│  ├─ ui/                                   # tokens (the production tailwind.css), shadcn primitives, Offside variants
│  ├─ ai/                                   # TS model router, prompt registry, telemetry (mirror of backend/apps/ai)
│  ├─ auth-utils/                           # JWT helpers, fetch interceptors, session hooks
│  ├─ workflows-sdk/                        # typed event names, action client, common step helpers
│  ├─ api-client/                           # generated TS client from OpenAPI (also publishes Swift client to frontend-ios/Generated)
│  └─ config/                               # shared eslint, tsconfig, prettier, tailwind preset
├─ tools/
│  ├─ openapi/                              # codegen scripts (TS + Swift)
│  └─ seeds/                                # demo seed scripts (Django management commands)
├─ PLAN.md                                  # this file
├─ README.md
├─ pnpm-workspace.yaml                      # frontend-web + packages/*
├─ turbo.json                               # optional; pnpm workspaces alone is fine
└─ package.json                             # root scripts (dev, build, test, codegen)
```

Notes:
- `frontend-ios` is *inside* the repo but *outside* the Node graph. A `tools/openapi/sync-ios.sh` copies the latest OpenAPI Swift client into `frontend-ios/Generated/` after every backend codegen.
- `backend/` is its own deployable. `Procfile` declares: `web: gunicorn ...`, `worker: celery -A offside_crm worker -l info`, `beat: celery -A offside_crm beat -l info`. DO App Platform reads the Procfile and provisions one component per process.
- The `backend/apps/ai/` Python module mirrors `packages/ai` TS — same prompt registry shapes, dual-language helpers. Server-side AI calls go through the Python module; UI-side AI calls (drafts, NL queries triggered from the browser) go through the TS module.
- Suite-app placeholders (`crunch-web`, `design-web`, `director-web`) are **included as 10-line Next.js shells**, each importing from `packages/ui` and rendering a "Coming soon" page that proves the package boundaries hold across products. They sit at the repo root alongside `frontend-web/`.

---

## 12. SaucyCart reuse map

`radianceskincare-app/saucycart-com-backend-django/` is a **reference**, not a fork. We do not copy code; we copy *patterns*.

| Pattern in SaucyCart | Reuse for Offside CRM | Notes |
|---|---|---|
| Custom email-based User (`core.CustomUser`) | Yes — match the field set | Replace SimpleJWT/Djoser flow with allauth + dj-rest-auth equivalents. |
| Multi-tenancy (`tenants.Tenant`, `TenantMembership`, `TenantMiddleware`) | Yes — adapt to `Workspace` / `Membership` | Tenant-scoped query mixin pattern is excellent. |
| `admin_crm.ClientRelationship` + `ClientNote` + signal-based denormalization | Inspirational | Replace with our Contact/Deal/Activity model; keep the signal pattern. |
| DigitalOcean Spaces storage | Yes (Spaces or Vercel Blob / Cloudflare R2) | Pluggable. Default to Spaces since we're DO-aligned. |
| `Procfile`-driven gunicorn deploy on DO App Platform | **Yes — exact deployment shape** | We add `worker:` and `beat:` lines for Celery. |
| Stripe scaffold | Defer past MVP | Billing is post-MVP. |
| Django Ninja + Pydantic | **Skip** — we standardize on DRF + drf-spectacular | OpenAPI tooling is more mature on DRF. |
| No Celery, no pgvector, no AI SDKs | Add fresh | Celery + pgvector + Anthropic. |
| No CI / no Docker | Add fresh | GitHub Actions + Dockerfile + docker-compose for local. |

---

## 13. Build sequence (15 milestones — revised for Celery)

Each milestone produces a working demo. Each ends with a commit. We ship in order. Sizes are rough; each is "1 senior dev, full focus."

| # | Milestone | Demo at the end | Rough size |
|---|---|---|---|
| 0 | **Repo scaffold** — pnpm workspaces, `frontend-web/` + `backend/` + `frontend-ios/` + `packages/*` + base configs + CI + brand tokens copied into `packages/ui` + `/brand` token-demo route in `frontend-web`. | Run `pnpm dev` (web) + `docker-compose up` (backend + Postgres + Redis): web app boots, Django admin loads, brand demo page renders, iOS project builds in Xcode. | 3 days |
| 1 | **Backend foundation** — fresh Django on Postgres+pgvector, allauth + dj-rest-auth + SimpleJWT, custom user, drf-spectacular emitting OpenAPI, Celery + Redis wired with a "ping" task, Procfile for DO. | `curl /api/auth/users/me/` returns 401 then 200 after login; `make celery-ping` returns from a worker; OpenAPI JSON served at `/api/schema/`. | 3 days |
| 2 | **Workspaces + multi-tenancy** — Workspace, Membership, Role, invite flow (email magic link via transactional email provider), workspace switcher in web, JWT carries `active_workspace_id`. | Sign up → create workspace → invite teammate → switch workspaces in the web app. | 4 days |
| 3 | **Web shell** — Next.js app shell with cmd palette skeleton, sidebar, top bar, keyboard nav, focus management, brand tokens applied, light-first theme. | Cmd-K opens; j/k navigates a placeholder list; tab order is sane; `/` focuses search. | 3 days |
| 4 | **Contacts + Companies** — CRUD, list view (saved-view stub), detail view, custom field defs (text/number/select/date), CSV import. | Import 1k contacts from CSV, paginate, edit a contact, custom fields render. | 4 days |
| 5 | **Deals + Pipelines + Tasks** — pipeline stages, kanban view, deal detail, tasks polymorphic to contacts/deals/companies. | Drag deal across stages; assign a task; activity log shows the change. | 4 days |
| 6 | **iOS shell + auth + read-only views** — SwiftUI app, OpenAPI Swift client, login, list contacts/deals, detail views. | Sign in on iOS, browse contacts, push notifications registered with APNs. | 5 days |
| 7 | **Workflow runtime v0** — `Automation` / `AutomationRun` / `AutomationStepRun` / `HitlRequest` models, "run advancer" Celery task, idempotency-keyed action handlers, Beat wake-up sweep, Django admin "Run inspector" view. | Programmatically create an automation that runs 3 steps including a 60-second delay; watch it transition `pending → running → awaiting_delay → running → completed` in the inspector after a worker restart in the middle. | 7 days |
| 8 | **Workflow node-graph editor v1** — React Flow canvas, palette of trigger/action/AI/logic nodes (subset), draft + publish, run history reads from automation_run. | Build a 4-step workflow ("when deal moves to Negotiation → wait 1 day → AI draft email → human approval"), publish, fire it. | 7 days |
| 9 | **Workflow engine completeness** — all triggers (record / time / webhook / form / Gmail / AI), all actions (mutations / Slack / Gmail send / HTTP / loop / branch / delay / approval), retries, run inspector enriched. | Demo a 10-step workflow with branch + loop + HITL approve-from-iOS-push. | 7 days |
| 10 | **Gmail + Calendar sync** — OAuth, message + thread + event sync, push notifications via Pub/Sub, "email received" trigger live, draft+send from contact view. | Reply to an email from inside Offside; thread summary appears in the contact's activity. | 7 days |
| 11 | **AI surfaces in CRM** — comms intelligence (drafts / replies / summaries), suggested next actions strip, lead scoring + enrichment workers, prompt telemetry visible. | Open a contact, see suggestions; auto-enrichment fills domain/size on a fresh company. | 6 days |
| 12 | **NL data layer + pgvector + global search** — NL → filter DSL, vector embeddings on notes/emails/summaries, hybrid search in cmd palette. | "Deals over $10k that went quiet last week" → results + AI summary; semantic search across notes works. | 5 days |
| 13 | **Agentic mode + HITL** — agent loop, agent-policy table, per-deal agent toggle, in-app + email + iOS push approval surface, undo window for reversible actions. | Toggle "Agent assist" on a deal; agent proposes 3 actions, one auto-executes, two require approval — approve from the iOS app. | 7 days |
| 14 | **Reports + saved views + dashboards (light)** — saved views with simple counters, deal funnel, activity over time. | Land on workspace home and see the team's pipeline + activity. | 4 days |
| 15 | **Polish pass** — empty states, loading states, error states, offline iOS handling, accessibility audit, Lighthouse pass on web, marketing-grade `/login` + `/signup` + landing route. | Walk every flow with axe-core open; Lighthouse ≥ 95 perf/a11y on web; iOS approves App Store review checklist locally. | 7 days |

Estimated total (single dev, no parallelism, no context-switch tax): ~83 working days ≈ **~16–19 weeks of focused build**. Honest realistic with team realities and unknowns: **5.5–7.5 months calendar time.** The Celery substitute adds about 1 milestone vs. the Inngest plan.

If you want to demo earlier, every milestone from #5 onward yields a usable internal release; #11 is the first one that genuinely *feels* like Offside.

---

## 14. Risks, open questions, outstanding asks

### 14.0 Locked at scaffold time (rev 3)
- **Suite placeholders** — **include** `crunch-web/`, `design-web/`, `director-web/` as 10-line shells from M0.
- **iOS folder** — **`frontend-ios/`** (mirrors `frontend-web/`).
- **Domain layout** — **`app.offside.ai`** (web) + **`crm-api.offside.ai`** (Django) + **`platform.offside.ai`** (marketing).
- **Transactional email** — **Resend**.

### 14.1 Open decisions (defer-able until the milestone they first matter)
- **Logo asset** — for M0 we use the existing OA monogram favicon. Full wordmark SVG needed by M3 (web shell). Path inside `OffsideLabs-AI/offsidelabs-ai-web/components/` to be confirmed, or fetched from the live site.
- **Per-product secondary hues** — proposed in §10 (clay / wheat / umber / deep-tan). Need only when each placeholder app gets real chrome; M0 uses the proposals.
- **Crunch / Design / Director letter** — proposed `C / X / D / R`. Confirm "X" for Crunch.
- **Stripe / billing** — post-MVP. Revisit before billing flows are needed.
- **APNs setup** — Apple Developer account + APNs key needed by M6. M0 scaffolds `frontend-ios/` with placeholder bundle ID.
- **DO App Platform spec** — sizes / region / Postgres + Redis tier. Decide before first deploy (post-M1).

### 14.2 Risks
- **Scope realism.** AMBITIOUS + native iOS day-one + autonomous agent + full workflow engine + a custom durable layer is many months. We've planned phasing carefully; the risk is loss of momentum if a milestone slips and demo cadence breaks.
- **Custom durable workflow layer.** Replacing Inngest costs us ~1.5 milestones of engine code (state machine, idempotency, run inspector, HITL primitive). The risk is subtle correctness bugs (lost runs, double-execution under retries). Mitigation: idempotency keys on every side effect; aggressive run-inspector tooling early (M7); chaos-testing the advancer with worker kills.
- **Styrene A licensing.** Display type isn't licensed yet. We render with the `Styrene A → Söhne → Inter` fallback chain. Brand-perfect typography requires the woff2 files dropped in.
- **Type chain weakness.** Without Drizzle/tRPC, type drift between Django and TS/Swift is a real risk. Mitigation: OpenAPI codegen runs on every PR, CI fails on drift.
- **AI cost.** Lead scoring + enrichment + embedding pipelines run on every new record. Without per-workspace budgets and provider fallback, costs blow up. Budget guardrails are in `packages/ai` and `backend/apps/ai/` from milestone 11.
- **Gmail Pub/Sub setup.** Requires GCP project + Pub/Sub topic + verified domain. ~1 day of unplanned setup if not already in place.
- **iOS distribution.** TestFlight + App Store review timeline is *not* in our 83-day estimate. Plan an extra 2–4 weeks of review/feedback cycles.
- **HITL trust.** Autonomous-then-approve UX is hard to get right. Milestone 13 has the highest UX-design risk in the plan.
- **Workflow-engine reconsideration trigger.** If the custom layer's complexity grows past ~milestone 9 (e.g., we need fan-out parallelism, complex retries, or sub-workflows), we should evaluate **Hatchet** (self-hostable, Postgres-backed, Inngest-class). Adding Hatchet is a swap of the executor — automation-graph storage stays in Django either way.

### 14.3 Outstanding asks (defer-able)
- Brand-perfect logo SVG export.
- Marketing-grade public site reuse from `OffsideLabs-AI/offsidelabs-ai-web` for `/login` + `/signup` aesthetic.
- Demo dataset (anonymized real-feeling contacts / deals) for milestone showcases.

---

## 15. Glossary

- **Workspace** — tenant boundary. All data is workspace-scoped.
- **Pipeline** — ordered set of deal stages owned by a workspace.
- **Activity** — append-only event row tied to a record (email, call, AI action, automation run, field change).
- **Automation** — user-authored workflow: trigger + graph of actions/conditions.
- **Run** — single execution of an automation. Walked by the run-advancer Celery task; durable state in Postgres.
- **Step run** — single node within a run. Tracks input/output/cost/latency/idempotency-key.
- **Run advancer** — the Celery task that owns the run-state machine. Loads the run row, executes the next step, persists state, re-enqueues itself or parks the run.
- **Wake-up sweep** — Celery Beat task that runs every minute and re-enqueues advancers for runs with `resume_at <= now()` or matching `awaiting_event_key`.
- **Agent policy** — per-workspace mapping of action type → mode (`suggest` / `approve` / `autonomous`).
- **HITL** — human-in-the-loop approval. Durable pause via `automation_run.status = awaiting_approval` + signed approval token.
- **OA monogram** — two overlapping tan circles. The suite mark.
- **Bone** — `#F1F1F1`. Light surface. Brand book calls it "paper"; production CSS calls it "bone." We use bone.
- **Tan** — `#C9A389`. The only saturated brand color. Emphasis only — never a fill.

---

*PLAN.md ends.*
