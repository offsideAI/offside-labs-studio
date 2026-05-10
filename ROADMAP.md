# Offside CRM — Roadmap (ROADMAP.md)

> Companion to [PRD.md](./PRD.md) and [PLAN.md](./PLAN.md). Each **phase maps 1:1 to an epic.** Inside an epic, work is broken into user stories (the "what" from a user's view) and engineering tasks (the "how"). Acceptance criteria match the milestone demo defined in PLAN.md §13. Cross-references to PRD `FR-N` / `NFR-N` and TESTING `TC-N` are noted on each phase.

**Status:** Draft v1. MVP phases mirror PLAN.md §13. Post-MVP phases are placeholders — real prioritization happens after MVP launch.
**Owner:** Offside Labs.
**Last revised:** 2026-05.

---

## Conventions

- **Phase / Epic ID:** `M-N` for MVP, `POST-N` for post-MVP placeholders.
- **Stories:** "As a [persona], I [action] so that [outcome]." Each story has a stable inline ID like `M2.S3` referenced in PR descriptions and TESTING.md cases.
- **Tasks:** engineering breakdown. Not exhaustive — focused on the load-bearing pieces. Routine work (lint, format, test scaffolding) is implicit.
- **Estimate:** working days for one focused senior engineer. Calendar time is roughly 1.7× this with normal coordination overhead.
- **Status:** `pending` / `in_progress` / `complete` updated as the project advances.

Color discipline reminder: every UI surface added in any phase MUST consume `packages/ui` tokens. No bespoke brand colors. (NFR-5)

---

## MVP

### Phase M0 — Repo scaffold (Epic: Repo Foundations)
*Status:* in progress (phase 1 of 2 done) · *Estimate:* 3 days · *Depends on:* — · *Covers:* infra · *Tests:* (smoke build only)

**User stories**
- M0.S1 — As an engineer, I can clone the repo and run `pnpm install && docker compose up && pnpm dev` and have all surfaces healthy locally.
- M0.S2 — As a designer, I can open `/brand` in any web app and see the live brand-token demo.
- M0.S3 — As an engineer, I can `pnpm ios:gen` and open the Xcode project that builds.

**Engineering tasks**
- pnpm workspace + Turborepo wiring; root configs (`.gitignore`, `.editorconfig`, prettier, turbo.json). *(done)*
- `packages/config` — shared tsconfig + Tailwind preset + Next base config. *(done)*
- `packages/ui` — brand tokens CSS adopted verbatim from offside.ai marketing site; Button / Card / Eyebrow / Hairline / StatusPill primitives. *(done)*
- `packages/{ai, auth-utils, workflows-sdk, api-client}` — typed scaffolds with stub exports. *(done)*
- `tools/openapi/codegen.mjs` — placeholder until M1's drf-spectacular schema is real. *(done)*
- `frontend-web/` — Next.js 15 app shell, `globals.css` importing tokens, `/brand` token-demo route, `next/font/google` for Roboto + JetBrains Mono. *(pending)*
- `crunch-web/`, `design-web/`, `director-web/` — 10-line shells importing `@offside/ui`. *(pending)*
- `backend/` — fresh Django 4.2 project, settings split (base/dev/prod), Celery wiring (`celery.py` + `app.autodiscover_tasks`), `Procfile` (web/worker/beat), `Dockerfile`, `docker-compose.yml` (postgres + redis + django + worker + beat). *(pending)*
- `frontend-ios/` — `Project.yml` (xcodegen), `OffsideCRMApp.swift`, `ContentView.swift`, README with Xcode steps. *(pending)*
- `.github/workflows/ci.yml` — lint + typecheck + Django tests + OpenAPI drift check. *(pending)*

**Acceptance criteria**
`pnpm dev` boots all 4 web apps; `pnpm backend:up` boots Django + Postgres + Redis + Celery; visiting `/brand` on each app renders the tokens demo without bespoke colors; `pnpm ios:gen && open frontend-ios/OffsideCRM.xcodeproj` opens an app that builds.

---

### Phase M1 — Backend foundation (Epic: Auth & API Plumbing)
*Status:* pending · *Estimate:* 3 days · *Depends on:* M0 · *Covers:* FR-2 (partial), NFR-3 · *Tests:* TC-1, TC-2, TC-3, TC-4

**User stories**
- M1.S1 — As a new user, I can sign up with email + password and receive a verification email.
- M1.S2 — As an engineer, I can hit `/api/schema/` and get a complete OpenAPI 3.1 document.
- M1.S3 — As an engineer, I can fire off a Celery `ping` task and see it executed by a worker.

**Engineering tasks**
- Postgres 16 + pgvector extension enabled; Django connects via `DATABASE_URL`.
- `apps/users` Django app — custom `User` (email-based, no username), allauth + dj-rest-auth wiring, SimpleJWT (access 1d, refresh 14d, blacklist on logout).
- Email backend wired to **Resend** via SMTP (or HTTP API); verification + password-reset templates.
- `drf-spectacular` for OpenAPI; `/api/schema/` + `/api/docs/` (Swagger).
- `offside_crm/celery.py` configured; Beat schedule loader pulling from a future `automations` app.
- Health endpoints `/health/live`, `/health/ready` (DB + Redis check).
- `tools/openapi/codegen.mjs` regenerates `@offside/api-client/src/generated/`.

**Acceptance criteria**
`POST /api/auth/registration/` → email verification → login → `/api/auth/users/me/` returns the user. `make celery-ping` returns from worker. `pnpm codegen:openapi` succeeds.

---

### Phase M2 — Workspaces + multi-tenancy + invite flow (Epic: Tenancy)
*Status:* pending · *Estimate:* 4 days · *Depends on:* M1 · *Covers:* FR-1, FR-24 partial · *Tests:* TC-5, TC-6, TC-7, TC-8

**User stories**
- M2.S1 — As a user, I can create a workspace from a sign-up landing.
- M2.S2 — As an owner, I can invite a teammate via Resend magic-link with a chosen role.
- M2.S3 — As a multi-workspace user, I can switch workspaces in ≤2 keystrokes.
- M2.S4 — As a backend engineer, I can trust that workspace isolation is enforced at the ORM layer and audited by tests.

**Engineering tasks**
- `apps/workspaces` Django app — `Workspace`, `Membership`, `Role` enum (`owner|admin|manager|rep|read_only`).
- `WorkspaceScopedMixin` Django ORM mixin; default manager filters by `request.workspace_id`.
- Custom DRF permission class checking `Membership.role` against per-view requirements.
- JWT custom claim `active_workspace_id`; refresh on switch.
- Invite flow — `Invitation` model, single-use token, Resend email, signup-with-token endpoint.
- `apps/auth-utils` (TS) — implement `authFetch` with refresh-on-401 + workspace switch.
- Web — workspace switcher in cmd-K (placeholder until M3 fleshes the palette).

**Acceptance criteria**
TC-5..TC-9 pass. Cross-workspace API calls return 403/404 (no leakage).

---

### Phase M3 — Web shell + cmd palette + keyboard nav (Epic: Web App Shell)
*Status:* pending · *Estimate:* 3 days · *Depends on:* M2 · *Covers:* NFR-1, NFR-2, foundation for FR-19 · *Tests:* TC-7, TC-55, TC-75, TC-76, TC-77

**User stories**
- M3.S1 — As any user, I can navigate the entire app with keyboard alone.
- M3.S2 — As a power user, I can press `Cmd+K` and reach any record / page in seconds.
- M3.S3 — As a screen-reader user, I can complete the core flows announced correctly.

**Engineering tasks**
- App shell layout — sidebar (collapsible), top bar (workspace switcher + user menu + global search trigger), main, slot for sub-nav.
- Cmd-K palette skeleton — fuzzy command match + workspace + record search hooks (real search lands M12).
- Keyboard nav primitives — `j/k` row nav, `/` focus search, `n` new, `esc` close modals.
- Focus management — focus-trap inside modals/popovers, focus-restore on close.
- Skip link, axe-clean smoke pass on shell.
- Brand surfaces — `/brand` token demo page (already from M0), `/login`, `/signup` chrome polished.

**Acceptance criteria**
TC-75..TC-79 pass (keyboard, reduced motion, skip link, axe, screen reader).

---

### Phase M4 — Contacts + Companies + Custom fields + CSV import (Epic: Core Records)
*Status:* pending · *Estimate:* 4 days · *Depends on:* M3 · *Covers:* FR-3, FR-4, FR-8, FR-20 (CSV slice) · *Tests:* TC-10..TC-14, TC-22..TC-24, TC-58, TC-84

**User stories**
- M4.S1 — As a rep, I can create / edit / archive contacts and companies.
- M4.S2 — As a rep, I can import 1k–5k contacts from CSV in 5 minutes with AI-suggested column mapping.
- M4.S3 — As an admin, I can define custom fields on contacts/companies (text/number/select/date).
- M4.S4 — As a rep, I can filter the contacts list by any standard or custom field.

**Engineering tasks**
- `apps/contacts`, `apps/companies` Django — models with workspace scoping, JSONB custom column, indexes on hot keys.
- `apps/custom_fields` — `CustomFieldDef` model + admin CRUD endpoints.
- Filter DSL v0 — JSON-encoded operator grammar (`{"and":[{"field":"lead_score","op":">","value":70}]}`); evaluator on Django side.
- List view (web) — virtualized table, column toggles, infinite scroll, saved-view stub.
- Detail view (web) — header, custom-fields panel, activity feed (read-only stub until M5).
- CSV import — workflow that reads CSV, AI maps columns to fields, user reviews mapping in a wizard, idempotent commit.

**Acceptance criteria**
TC-10..TC-14, TC-22..TC-24, TC-58, TC-84 pass.

---

### Phase M5 — Deals + Pipelines + Tasks + Notes + Activities (Epic: Pipeline & Records v2)
*Status:* pending · *Estimate:* 4 days · *Depends on:* M4 · *Covers:* FR-5, FR-6, FR-7 · *Tests:* TC-15..TC-21

**User stories**
- M5.S1 — As a manager, I can define a pipeline with custom stages and assign deals to it.
- M5.S2 — As a rep, I can drag deals across stages on a kanban view.
- M5.S3 — As a rep, I can attach tasks and notes to any record (contact / company / deal).
- M5.S4 — As any user, I see a chronological activity feed on every record.

**Engineering tasks**
- `apps/deals` — `Deal`, `Pipeline`, `Stage` (ordered JSONB on Pipeline) models.
- `apps/tasks` — `Task` model with polymorphic `(related_type, related_id)`.
- `apps/notes` — `Note` (Markdown body) + 24h edit window enforcement.
- `apps/activities` — `Activity` append-only event log; signal hooks on Deal/Contact/Company/Task save fire activity rows.
- Web — kanban (DnD-kit), deal detail, tasks tab, notes tab, activity feed (real now).

**Acceptance criteria**
TC-15..TC-21 pass.

---

### Phase M6 — iOS shell + auth + read-only views (Epic: iOS Foundation)
*Status:* pending · *Estimate:* 5 days · *Depends on:* M5 · *Covers:* FR-23 (partial), NFR-1 · *Tests:* TC-68, TC-71, TC-88

**User stories**
- M6.S1 — As a rep, I can log in on iOS with my web credentials.
- M6.S2 — As a rep, I can browse contacts, companies, deals, tasks on iOS read-only.
- M6.S3 — As a rep, the app caches my last 50 visited records for offline read.

**Engineering tasks**
- `frontend-ios` SwiftUI app — login screen, JWT in Keychain, refresh-on-401 interceptor.
- OpenAPI Swift codegen (`tools/openapi/sync-ios.sh`) wired into Xcode build phase.
- List + detail screens for Contact / Company / Deal / Task using generated client.
- Local cache (SwiftData or simple JSON-file cache) for offline read of last 50 records.
- APNs registration + token round-trip to backend (real push lands M13).
- Pull-to-refresh + skeleton loading + offline banner + retry button.

**Acceptance criteria**
TC-68, TC-71, TC-88 pass. App Store review checklist locally green.

---

### Phase M7 — Workflow runtime v0 (Epic: Durable Workflow Engine)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M5 · *Covers:* FR-11 (foundation), NFR-7 · *Tests:* TC-33, TC-34, TC-39

**User stories**
- M7.S1 — As an engineer, I can author a workflow as JSON, persist it as `Automation`, and watch a `run_advancer` Celery task walk it durably.
- M7.S2 — As an admin, the run inspector in Django admin shows me every step's input / output / cost / latency.
- M7.S3 — As an SRE, when I kill a worker mid-step, the workflow recovers without duplicate side effects.

**Engineering tasks**
- `apps/automations` Django — `Automation`, `AutomationRun`, `AutomationStepRun`, `HitlRequest`, `AgentPolicy` models with statuses per PLAN §6.
- `automations.tasks.run_advancer(run_id)` Celery task — SELECT FOR UPDATE on the run row, execute next step, persist state, re-enqueue or park.
- Idempotency: action handlers look up `(run_id, step_id, attempt)` and short-circuit on cached output.
- Beat task `wake_up_sweep` — every 60s, enqueue advancers for runs with `resume_at <= now()` or matching `awaiting_event_key`.
- Action handler registry — `@action("crm.create_contact")` decorators map kind → callable.
- Run inspector view in Django admin — list, detail, manual replay/cancel actions.
- HITL primitive — `HitlRequest` row + signed JWT approval token + `/api/hitl/<token>/decide` endpoint.

**Acceptance criteria**
TC-33, TC-34, TC-39 pass. Programmatically created 3-step workflow with delay survives a worker kill mid-delay.

---

### Phase M8 — Workflow node-graph editor v1 (Epic: Visual Authoring)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M7 · *Covers:* FR-12 (partial) · *Tests:* TC-29, TC-30, TC-31, TC-32

**User stories**
- M8.S1 — As an admin, I can build a workflow visually with React Flow.
- M8.S2 — As an admin, I can save drafts and publish versioned workflows.
- M8.S3 — As an admin, I can describe a workflow in English and have Claude generate the graph.

**Engineering tasks**
- React Flow canvas — node palette (subset: trigger, AI step, action, branch, delay, approval, end).
- Node config drawer — per-node form driven by the node's schema.
- Save draft + publish flow — version bump on publish; in-flight runs continue on their original version.
- "Describe in English" panel — Claude prompt `automations.author_from_nl.v1` returns JSON graph; canvas hydrates.
- Undo/redo on canvas edits.
- Schema validator — disconnected nodes, missing required fields, type mismatches between adjacent nodes.

**Acceptance criteria**
TC-29..TC-32 pass.

---

### Phase M9 — Workflow engine completeness (Epic: Triggers, Actions, Integrations)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M8 · *Covers:* FR-11 (full), FR-21, FR-22 · *Tests:* TC-39, TC-62..TC-65, TC-83

**User stories**
- M9.S1 — As an admin, I can use any of the v1 trigger types (record, time, webhook, form, AI condition).
- M9.S2 — As an admin, I can use any v1 action type (CRM mutate, Slack, HTTP, branch, loop, delay, approval).
- M9.S3 — As an admin, I can post to Slack channels/DMs from any workflow.

**Engineering tasks**
- Trigger registry — webhook (HMAC), form-submission endpoint, schedule (Beat-driven), Gmail Pub/Sub stub (real in M10).
- Action registry — CRM mutations across all M5 entities; Slack action via OAuth integration; HTTP request with auth presets; loop-over-list step; branch step.
- Slack OAuth + connection model in `apps/integrations`.
- Run inspector enriched — node graph viewer, retry counts, idempotency keys visible.

**Acceptance criteria**
TC-62..TC-65, TC-39, TC-83 pass. 10-step workflow with branch + loop + HITL approve-from-iOS-push works end-to-end.

---

### Phase M10 — Gmail + Calendar sync (Epic: Comms Source-of-Truth)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M9 · *Covers:* FR-9, FR-10 · *Tests:* TC-25..TC-28, TC-41

**User stories**
- M10.S1 — As a rep, I connect my Gmail and see threads with each contact within a minute.
- M10.S2 — As a rep, replies arrive in the contact's activity feed in real time.
- M10.S3 — As a rep, I send email from the contact view as my Gmail account.
- M10.S4 — As a rep, I see GCal meetings on each deal.

**Engineering tasks**
- Gmail OAuth (read + send + push scopes); thread + message ingestion service.
- Pub/Sub topic + subscription + verified domain; `/gmail/push` endpoint.
- Send-mail action wired to Gmail API.
- Threading: matching algorithm to associate threads with contact emails.
- GCal OAuth + event sync (read + write).
- "Email received" workflow trigger; `email_sent` activity rows from outbound.

**Acceptance criteria**
TC-25..TC-28, TC-41 pass.

---

### Phase M11 — AI surfaces in CRM (Epic: AI Everywhere v1)
*Status:* pending · *Estimate:* 6 days · *Depends on:* M10 · *Covers:* FR-13, FR-15, FR-16, NFR-6 · *Tests:* TC-40..TC-42, TC-46..TC-50, TC-86, TC-91

**User stories**
- M11.S1 — As a rep, AI drafts and reply-suggestions appear inline in every contact + deal view.
- M11.S2 — As a rep, new contacts and companies auto-enrich (industry, size, score) within 60 seconds.
- M11.S3 — As a rep, quiet deals show calm "next-action" suggestions I can dismiss or convert to a workflow.

**Engineering tasks**
- `packages/ai` — real model router (Claude default; OpenAI/Gemini fallback), prompt registry, structured-output retry-with-correction, telemetry emitter.
- `backend/apps/ai` — Python twin with the same prompt names + Pydantic schemas.
- Prompts: `comms.draft_reply.v1`, `comms.summarize_thread.v1`, `comms.summarize_meeting.v1`, `enrichment.company.v1`, `scoring.lead.v1`, `suggestions.next_action.v1`.
- Streaming surface in web — server-sent events through Next.js route handler.
- Per-workspace daily token budget; over-budget queue + admin notice.
- Provider fallback wiring; "fallback model" badge in admin telemetry.

**Acceptance criteria**
TC-40..TC-42, TC-46..TC-50, TC-86, TC-91 pass.

---

### Phase M12 — NL data layer + pgvector + global search (Epic: Conversational Data Access)
*Status:* pending · *Estimate:* 5 days · *Depends on:* M11 · *Covers:* FR-14, FR-19 · *Tests:* TC-43..TC-45, TC-55..TC-57

**User stories**
- M12.S1 — As a manager, I type natural-language queries in cmd-K and see a filtered list within 2 seconds.
- M12.S2 — As a rep, fuzzy queries like "deals that smelled risky" still find the right results via vector rerank.
- M12.S3 — As a rep, my saved NL views persist and are shareable with my workspace.

**Engineering tasks**
- Embedding worker — Celery task on entity create/update writes to `embedding` table with HNSW index.
- Prompt `data.nl_to_filter_dsl.v1` — schema-aware (includes custom fields), schema cached per workspace per schema version.
- Filter DSL evaluator promoted to a first-class server-side endpoint `/api/query/`.
- Hybrid search: FTS first; vector rerank when FTS confidence is low.
- Saved views in cmd-K (sharing semantics: workspace-visible by default; private if marked).

**Acceptance criteria**
TC-43..TC-45, TC-55..TC-57 pass.

---

### Phase M13 — Agentic mode + HITL (Epic: Agent Autonomy v1)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M12 · *Covers:* FR-17, completes FR-23 push · *Tests:* TC-37, TC-38, TC-51..TC-54, TC-70

**User stories**
- M13.S1 — As an admin, I can set per-action-type policies (`suggest` / `approve` / `autonomous`) for the workspace.
- M13.S2 — As a rep, I can toggle "Agent assist" on a specific deal and see the agent propose actions.
- M13.S3 — As a manager, I receive iOS pushes for HITL approvals and can act without unlocking the device.
- M13.S4 — As any user, autonomous reversible actions show a 60-second undo affordance.

**Engineering tasks**
- Agent policy table UI + persistence.
- Agent loop — Claude Opus planner returns proposed actions; per-action policy gates dispatch; HITL fans out to in-app + email + iOS push.
- iOS push notification actions — Approve / Reject / Snooze (deferred 1h) on lock-screen.
- Undo system — for reversible action types, expose a 60s undo toast; record undo in activity.
- Audit row enrichment — every agent action logs prompt + model + cost + decider + decision.

**Acceptance criteria**
TC-37, TC-38, TC-51..TC-54, TC-70 pass.

---

### Phase M14 — Reports + saved views + dashboards (Epic: Visibility)
*Status:* pending · *Estimate:* 4 days · *Depends on:* M13 · *Covers:* FR-18 · *Tests:* TC-72..TC-74

**User stories**
- M14.S1 — As a manager, on workspace home I see this week's pipeline + the team's activity.
- M14.S2 — As a viewer, I can drill from a counter into the underlying records.

**Engineering tasks**
- Workspace home dashboard — counters (deals by stage, won this month, overdue tasks), funnel chart, activity-over-time chart.
- Cached aggregates — periodic Beat task refreshes (every 5 min) writes to a `dashboard_cache` table.
- Charting library — Tremor or Visx (decision deferred to phase start; both work with brand tokens).
- Saved views surfaced on workspace home.

**Acceptance criteria**
TC-72..TC-74 pass.

---

### Phase M15 — Polish (Epic: Production Readiness)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M14 · *Covers:* NFR-1, NFR-2, NFR-4 · *Tests:* TC-78, TC-79, TC-80..TC-87 across the suite

**User stories**
- M15.S1 — As any user, every flow has thoughtful empty / loading / error states.
- M15.S2 — As any user, the marketing-grade `/login` + `/signup` + landing route feels like a polished product.
- M15.S3 — As an SRE, every page meets perf budgets; Lighthouse ≥ 95.

**Engineering tasks**
- Empty-state inventory across every route; design + copy pass.
- Loading skeletons on every async surface (no blank flash).
- Error boundary + toast system; provider fallback messaging.
- Lighthouse / axe runs in CI; fail-the-build threshold set.
- iOS regression sweep; offline edits with conflict-resolution polish.
- Marketing-grade `/login` + `/signup` reusing offside.ai marketing-site shell.

**Acceptance criteria**
TC-78..TC-88 pass. Lighthouse ≥ 95 perf/a11y on web. iOS App Store review checklist green.

---

## Post-MVP placeholders

Each phase below is a **placeholder**. Real prioritization happens after MVP launch + first-cohort interviews. Order is not committed — it's a working hypothesis. Engineering effort is "T-shirt" sized only.

### Phase POST-1 — Stripe / billing
*Covers PRD:* POST-1 · *Size:* L · *Depends on:* M15
- Plan tiers (Free trial → Starter → Team → Scale).
- Per-seat pricing + AI-token soft caps; metering of token usage to Stripe.
- Customer portal for self-serve plan changes.
- Dunning + grace period; workspace lockout on chronic non-payment.
- Webhook handler for invoice.paid / subscription.updated.
- Open question: usage-based vs hybrid pricing — needs price-test infra (POST-15 marketplace might cover).

### Phase POST-2 — Long-tail integrations
*Covers PRD:* POST-2 · *Size:* XL (multi-quarter) · *Depends on:* M15
- HubSpot bidirectional sync (read + write back).
- Salesforce read-only mirror + selective write.
- Microsoft 365 — Outlook + Calendar parity to Gmail/GCal.
- Linear, Notion, Zoom, Twilio (SMS/calls), DocuSign.
- Pattern: each integration = OAuth + ingestion service + webhook handler + workflow trigger/action set + a connector card in Settings.

### Phase POST-3 — Multi-language i18n (web + iOS)
*Covers PRD:* POST-3 · *Size:* L · *Depends on:* M15
- ICU message format; translation pipeline (Crowdin / Lokalise).
- RTL support evaluation — likely punted to a later phase.
- Date/number locale handling.
- AI prompts respect user locale (German rep gets German drafts).

### Phase POST-4 — Native Android app
*Covers PRD:* POST-4 · *Size:* XL · *Depends on:* M15, partial POST-3
- Decision: Kotlin Multiplatform (share with iOS where possible) vs native Compose.
- APNs equivalent: FCM.
- Re-test full E2E suite per TESTING.md on Android targets.

### Phase POST-5 — Enterprise: SSO/SCIM/audit/sandbox
*Covers PRD:* POST-5 · *Size:* L · *Depends on:* M15
- SAML/OIDC SSO (WorkOS or built-in).
- SCIM provisioning.
- 7-year audit retention with object-storage cold tier.
- Custom role builder (granular permission matrix).
- Per-workspace sandbox environment (separate Postgres schema + Redis namespace).

### Phase POST-6 — Suite app: Crunch (AI-native spreadsheet)
*Covers PRD:* POST-6 · *Size:* XL · *Depends on:* M15
- New `frontend-web` sibling app at `crunch-web/`. Shared `packages/ui`, `packages/ai`, `packages/auth-utils`.
- Distinct backend or new Django app inside `backend/` (decision deferred — likely separate service to keep CRM stable).
- Spreadsheet engine — formula evaluator, AI-cell with prompt registry.

### Phase POST-7 — Suite app: Design (AI-native app design tool)
*Covers PRD:* POST-7 · *Size:* XL · *Depends on:* POST-6 (Crunch shakes out shared-package gaps first)
- Canvas + design system primitives (`@offside/ui` extended with editor surfaces).
- AI primitives: layout generator, copy generator, theme generator.

### Phase POST-8 — Suite app: Director (AI-native marketing suite)
*Covers PRD:* POST-8 · *Size:* XL · *Depends on:* POST-6, POST-7
- Campaign builder, audience segments (re-use CRM contact schema), AI ad-copy + creative.
- Cross-product data model: CRM contact = Director audience member.

### Phase POST-9 — Advanced agent capabilities
*Covers PRD:* POST-9 · *Size:* L · *Depends on:* M15
- Multi-step planning across many records ("warm up 50 leads this week with personalized outreach").
- Agent-to-agent handoff for complex cross-functional flows.
- Voice-call agents (Twilio + AI).
- Autonomous prospecting from public data.

### Phase POST-10 — Workflow advanced features
*Covers PRD:* POST-10 · *Size:* L · *Depends on:* M15
- Sub-workflows (call workflow A from workflow B with typed I/O).
- Parallel fan-out + join steps.
- Conditional rollout (run new version on 10% of records before full deploy).
- Workflow templates marketplace (community-contributed).
- Durable workflow versioning beyond MVP semantics.

### Phase POST-11 — Reporting v2
*Covers PRD:* POST-11 · *Size:* L · *Depends on:* M15
- Custom dashboard builder (drag-drop chart blocks).
- Scheduled report email (PDF + CSV).
- Formula fields and lookup fields on entities.
- BI-quality drill-down + pivoting.
- CSV/Excel export from any list view.

### Phase POST-12 — Mobile features (iPad, Watch, Catalyst, offline-first edits)
*Covers PRD:* POST-12 · *Size:* L · *Depends on:* M15
- iPad-optimized layouts with multi-column.
- Apple Watch complications for "today" + push-approve.
- Mac Catalyst.
- Offline-first edits with conflict resolution (merge strategy per field).
- Full-text search on-device.

### Phase POST-13 — Compliance & data residency
*Covers PRD:* POST-13 · *Size:* XL · *Depends on:* POST-5
- SOC 2 Type 2 audit prep.
- ISO 27001.
- GDPR DPA + EU data residency.
- HIPAA where vertical-relevant (healthcare sales orgs).
- Region-specific deployments (Postgres replicas in EU/APAC).

### Phase POST-14 — Public API + developer portal
*Covers PRD:* POST-14 · *Size:* M · *Depends on:* M15
- API tokens per workspace with scopes.
- Public OpenAPI spec at `developers.offside.ai`.
- Sample SDKs (TypeScript, Python).
- Developer docs site.
- Rate limiting + usage analytics per token.

### Phase POST-15 — Marketplace + extensions
*Covers PRD:* POST-15 · *Size:* L · *Depends on:* POST-14
- Custom workflow nodes contributed by partners (sandboxed execution).
- Workspace-installable AI prompts.
- Branded automation templates.
- Revenue share for paid extensions (depends on POST-1 billing).

---

## Phase dependency graph (MVP)

```
M0 ──► M1 ──► M2 ──► M3 ──► M4 ──► M5 ──► M6
                                   │
                                   └──► M7 ──► M8 ──► M9 ──► M10 ──► M11 ──► M12 ──► M13 ──► M14 ──► M15
```
- M6 (iOS) and M7 (workflow runtime) both depend on M5 but are otherwise independent.
- M11 (AI surfaces) explicitly depends on M10 (Gmail/GCal) so meeting + thread summaries have real data.
- M13 (agent + HITL) explicitly depends on M12 (NL data layer) so the planner has access to schema-aware queries.

## Total MVP estimate

| Phase | Days |
|---|---|
| M0  | 3 |
| M1  | 3 |
| M2  | 4 |
| M3  | 3 |
| M4  | 4 |
| M5  | 4 |
| M6  | 5 |
| M7  | 7 |
| M8  | 7 |
| M9  | 7 |
| M10 | 7 |
| M11 | 6 |
| M12 | 5 |
| M13 | 7 |
| M14 | 4 |
| M15 | 7 |
| **Total** | **83 days** |

Calendar projection (single senior eng, normal coordination overhead): **~16–19 weeks** of focused build → **5.5–7.5 months**. Earliest demo-credible internal release: end of M5 (~5 weeks). Earliest "feels like Offside" milestone: end of M11 (~12 weeks).

---

## Status updates

This file gets a one-line status tick at the top of each phase as the project advances. Substantive scope changes get a `## Revision N — date` block at the bottom describing the diff.

---

*ROADMAP.md ends.*
