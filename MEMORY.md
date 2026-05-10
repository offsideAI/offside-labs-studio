# MEMORY.md

> Running record of project state, locked decisions, and watch-outs. Companion to [PLAN.md](./PLAN.md) / [PRD.md](./PRD.md) / [TESTING.md](./TESTING.md) / [ROADMAP.md](./ROADMAP.md) — but **more living**. Update as state changes.

## Current state (2026-05)

- **Branch:** `main`. Up to date with `origin/main` through `9bd7e27`. M0–M7 all shipped and pushed; doc-sync commit (PRD/ROADMAP checkboxes) pending in working tree.
- **Latest commits (newest first):**
  - `9bd7e27` Update MEMORY.md: M7 complete; M8 (workflow node-graph editor v1) is next
  - `e69dfa3` M7: workflow runtime v0 — apps/automations + run_advancer + idempotency + HITL
  - `eeef2cb` Update MEMORY.md: M6 complete; M7 (workflow runtime v0) is next
  - `6d33a60` M6: iOS shell — auth + workspace picker + read-only contact/company/deal views
  - `c3507b1` Update MEMORY.md: M5 fully complete; M6 (iOS shell) is next
  - `f428a47` M5 frontend: deals kanban + tasks/notes/activity tabs + integrated record feeds
  - `9254b8d` Update MEMORY.md to reflect M5 backend complete (frontend pending)
  - `66ab096` M5 phase 2: apps/tasks + apps/notes + apps/activities + signal handlers
  - `12b53e9` M5 phase 1: apps/deals — Pipeline + Deal + filter DSL reuse
  - `03c692b` Update MEMORY.md to reflect M4 complete + M5 ready to start
  - `b34ebec` M4 CSV import: apps/imports + heuristic mapper + Celery task + wizard
  - `41b14ce` M4 frontend: contacts + companies + custom-fields settings (CSV import next)
  - `13a85ce` M4 backend: apps/companies + apps/contacts + apps/custom_fields + filter DSL
  - `36884a9` Update MEMORY.md to reflect M3 complete + M4 ready to start
  - `b4fdaa7` M3: AppShell + cmd-K palette + keyboard primitives + settings page (TC-6 + TC-9 closure)
  - `96ff3fd` Update MEMORY.md to reflect M2 complete + M3 ready to start
  - `5ee2c33` M2 frontend: auth-utils real impl + login/signup/onboarding/accept-invite + workspace shell
  - `d9cc5ec` M2 backend: apps/workspaces — Workspace + Membership + Invitation + role-based perms
  - `11b785f` Update MEMORY.md to reflect M1 complete + M2 ready to start
  - `4ed442e` M1: backend foundation — apps/users + auth wiring + real OpenAPI codegen
  - `268922c` Update MEMORY.md to reflect M0 complete + M1 ready to start
  - `d48c5ed` Complete M0 scaffold: backend (Django + Celery + DO Procfile) + iOS (xcodegen + SwiftUI) + CI
  - `dd2a003` Scaffold M0 phase 2a — web surface (frontend-web + three suite placeholders)
  - `0090063` Add CLAUDE.md and MEMORY.md for durable repo-level context
  - `5375384` Scaffold Offside CRM monorepo with planning docs and shared packages
- **Milestone status:**
  - **M0 — complete.** Repo skeleton resolves end-to-end: `pnpm install`, `pnpm dev` (4 web apps), `pnpm backend:up` (Postgres+pgvector + Redis + Django + worker + beat), `pnpm ios:gen` (Xcode project), GitHub Actions CI.
  - **M1 — complete.** `apps/users` (email-based custom User) + allauth + dj-rest-auth + SimpleJWT at `/api/auth/*` + public OpenAPI schema + real openapi-typescript codegen. Tests: signup → login → /api/auth/user/ + Celery ping smoke + schema-served.
  - **M2 — complete.** `apps/workspaces` (Workspace + Membership + Role + Invitation) + role-based permissions + WorkspaceJWTAuthentication via X-Workspace-Id header + Resend magic-link invites. Frontend: login + signup + onboarding + accept-invite + protected /[workspace]/ route group with TanStack Query v5.
  - **M3 — complete.** AppShell + cmd-K palette (cmdk) + useKeyboardShortcut hook (Cmd-K / "/" / Esc, input-aware). Settings page closes TC-6 (admin role promotion) + TC-9 (owner archive). Six new backend tests.
  - **M4 — complete.** `apps/companies` + `apps/contacts` + `apps/custom_fields` + `apps/imports` ship the records surface. Filter DSL v0 (JSON → Django Q with custom-field JSONB lookups). Frontend: contact + company list/new/detail pages, custom-fields settings (admin), CSV import wizard (upload → mapping review → commit → poll progress) with heuristic header mapper. CustomFieldsPanel renders typed inputs (text/number/select/date/etc) per CustomFieldDef. Hand-authored 0001 migrations for all four apps. Tests: 14 new — contact CRUD + filter DSL + custom field defs + CSV upload + commit + admin-only.
  - **M5 — complete.** Backend: apps/deals (Pipeline + Deal with stages JSONB on Pipeline + stage_id slug + filter DSL reuse), apps/tasks (polymorphic + status/priority enums + completed_at auto-stamp), apps/notes (Markdown + 24h edit window + audit), apps/activities (append-only + signal handlers on Contact/Company/Deal save + DEAL_STAGE_CHANGED). Shared RelatedType/ActivityKind/ActorKind enums in apps.activities.types. 17 new backend tests. Frontend: /[workspace]/deals/ DnD-kit kanban with optimistic stage_id PATCH on drag, deal new + detail pages, ActivityFeed + TasksTab + NotesTab reusable components integrated on contact + company + deal detail (replacing M4's "Coming in M5" stub). Sidebar Deals live; cmd-K reaches Deals.
  - **M6 — complete.** SwiftUI iOS client replaces the M0 brand-parity placeholder. Auth: KeychainStore wraps SecItem for JWT persistence; AuthStore (`@Observable`) holds `.unknown / .signedOut / .needsWorkspace / .ready(workspace)` state and bootstraps from Keychain on launch. Networking: APIClient singleton mirrors authFetch — Bearer + X-Workspace-Id + retry-on-401 with refresh; baseURL reads from Info.plist's OffsideApiBaseUrl with localhost ATS exception declared in Project.yml. Views: ContentView routes to LoginView / WorkspacePickerView / MainTabView; MainTabView gives Contacts / Companies / Deals / More tabs with `@Observable` list models, NavigationStack push to detail views, pull-to-refresh, ErrorBanner overlay, brand-correct StatusPill / Eyebrow / EmptyStateView components. Deal rows resolve stage_id → label against the workspace's pipelines. Editing, custom-fields panel, tasks/notes/activity feeds, push notifications, and OpenAPI Swift codegen are explicitly deferred (M13 push, codegen wiring is a follow-up commit).
  - **M7 — complete.** apps/automations ships the durable workflow state machine (PLAN.md §7). Models: Automation + AutomationRun + AutomationStepRun + HitlRequest + AgentPolicy with status/run-state enums and the all-important `idempotency_key` unique constraint on AutomationStepRun. graph.py defines the JSON schema (action / delay / approval / branch / wait_for_event / end), template resolution (`{{ a.b.c }}` against state_snapshot), branch-condition evaluation. actions.py is the @register-decorated dispatcher with built-ins (noop, log, crm.create_contact, crm.move_deal_stage). tasks.py owns run_advancer (SELECT FOR UPDATE on the run row, idempotency-key short-circuit on replay, tail-recursive re-enqueue) + wake_up_sweep + resume_after_hitl. hitl.py wraps PyJWT for purpose-claim'd approval tokens with 7-day default TTL. Django admin gets a Run Inspector with inline AutomationStepRun rows. 14 new tests including the load-bearing replay-doesn't-double-create-contact (TC-34 chaos slice) + wake-up sweep round-trip + approval routing. CELERY_BEAT_SCHEDULE documents the wake_up_sweep entry pending a PeriodicTask data migration.
  - **M8 — pending (next).** Workflow node-graph editor v1 (React Flow). Frontend canvas with palette + node config drawer + draft/publish + describe-in-English Claude prompt. Maps to TC-29..TC-32.
  - **M8–M15 — pending.** Per [ROADMAP.md](./ROADMAP.md).

## Locked decisions (interview Rounds 1–7)

Captured exhaustively in PLAN.md §5.1 and §14.0. The non-obvious ones:

- **Drizzle and tRPC dropped.** Hybrid Next.js + Django stack means OpenAPI codegen is the type chain.
- **Auth = django-allauth + dj-rest-auth + SimpleJWT** (NOT Djoser, despite SaucyCart using Djoser).
- **API framework = DRF** (NOT Django Ninja, despite SaucyCart using Ninja). drf-spectacular for OpenAPI.
- **Workflow engine = Celery + Redis + custom Django durable layer** (NOT Inngest — DO App Platform constraint). See PLAN.md §7.
- **Hosting:** Vercel (web) + Digital Ocean App Platform (Django web/worker/beat) + DO Managed Postgres + DO Managed Redis.
- **Monorepo layout:** flat. `frontend-web/`, `backend/`, `frontend-ios/`, `packages/*`, three suite placeholders. **No `apps/*` prefix.**
- **iOS folder:** `frontend-ios/` (mirrors `frontend-web/`).
- **Domains:** `app.offside.ai` (web) + `crm-api.offside.ai` (Django) + `platform.offside.ai` (marketing).
- **Transactional email:** Resend.
- **Brand:** OffsideAI Design System v1.0 + production CSS at `OffsideLabs-AI/offsidelabs-ai-web/assets/css/tailwind.css` (adopted verbatim into `packages/ui/src/styles/tokens.css`). Tan/Ink/Bone palette; light-first; Styrene A → Söhne → Inter / Roboto / JetBrains Mono.
- **MVP scope:** AMBITIOUS. Every Round 1–3 feature shipped across 16 milestones. No de-scoping by default.
- **Agent autonomy:** default-suggest, opt-in autonomous per action type. HITL via in-app + email + iOS push.

## Outstanding non-blocking decisions (PRD §9, PLAN §14.1)

- Full logo SVG (favicon already used; full wordmark needed by M3 web shell).
- Per-product secondary hues (proposals in PLAN §10 — clay/wheat/umber/deep-tan).
- Crunch's letter ("X" proposed for X-axis spreadsheet metaphor; unconfirmed).
- Stripe / billing — post-MVP per POST-1.
- APNs key — needed by M6 (iOS shell).
- DO App Platform sizes — needed at first deploy (post-M1).

## Watch-outs

- **Brand book's `#B8916F` fails WCAG (2.54:1 on Bone).** Production CSS uses `#7A5F44`. **Don't "correct" back.**
- **Custom durable workflow layer is a real engineering risk.** Mitigations:
  - Idempotency keys `(run_id, step_id, attempt)` on every side effect.
  - Chaos-test worker kills mid-run early in M7.
  - Run-inspector tooling visible from M7, not delayed.
  - **Hatchet** is the explicit fallback if M9 reveals the layer's complexity is growing past plan.
- **Styrene A is paid (Commercial Type license).** Default ships with Söhne→Inter fallback. Drop woff2 files into `frontend-web/public/fonts/` to activate; the production CSS already lists Styrene A first in the stack.
- **Gmail Pub/Sub setup** requires GCP project + Pub/Sub topic + verified domain. Plan ~1 day of unplanned setup before M10.
- **iOS App Store review timeline** is NOT in the 83-day estimate. Add 2–4 weeks for review/feedback cycles.
- **Type-chain weakness without Drizzle/tRPC.** Mitigation: OpenAPI codegen runs on every PR; CI fails on schema drift. Don't let this slip.
- **AI cost guardrails.** Lead scoring + enrichment + embedding pipelines run on every record write. Per-workspace daily token budgets land in M11; provider fallback (Claude → OpenAI/Gemini) is in `packages/ai`. **Don't ship AI features without these guardrails wired up.**
- **HITL trust.** The autonomous-then-approve UX in M13 has the highest UX-design risk in the plan.

## SaucyCart reuse boundary

Located at `../radianceskincare-app/saucycart-com-backend-django/`. **Reference only — no code copy.**

| Pattern | Reuse? |
|---|---|
| Custom email-based User | ✓ pattern; we re-implement under allauth |
| Multi-tenancy (Tenant / Membership / Middleware) | ✓ pattern; we adapt to Workspace / Membership |
| `admin_crm` signal-based denormalization | ✓ pattern |
| DigitalOcean Spaces storage | ✓ default for media |
| Procfile + gunicorn + DO App Platform | ✓ exact deployment posture |
| Djoser + SimpleJWT | ✗ replaced with allauth + dj-rest-auth |
| Django Ninja | ✗ replaced with DRF |
| Their domain (services / bookings / providers) | ✗ irrelevant to CRM |
| Lack of Celery / pgvector / AI SDKs / Docker / CI | ✗ all added fresh |

## User decision style (working notes)

(Detailed in agent memory; abbreviated here.)

- Picks **ambitious over conservative** every time. "Recommended" labels are context, not nudges.
- Pastes **large brand/spec content** when they want it adopted wholesale (the OffsideAI Design System v1.0 paste landed mid-Round-7 and overrode Round 5's dark-first/violet/Inter answers).
- Pivots major architectural decisions mid-stream. When this happens, **update PLAN.md thoroughly** before more code lands.
- Says "pause" deliberately when they actually want to inspect or commit. Treat literal pause as a literal pause.

## Resume points

M7 is complete. **Next milestone is M8 (workflow node-graph editor v1 — React Flow).**

Verify M7 locally first:
1. `pnpm backend:up` + `pnpm backend:migrate` (apps/automations 0001 migration creates Automation/AutomationRun/AutomationStepRun/HitlRequest/AgentPolicy) + `pnpm backend:test` (14 new automation tests including chaos-replay + wake-up sweep round-trip).
2. Django admin → Automations → create a tiny graph (`start → action: noop → end`) → manually create an AutomationRun → confirm `run_advancer` walks it to `COMPLETED` and AutomationStepRun rows show input/output/cost/latency.
3. Hit HITL: change the noop to an `approval` node → run → confirm status flips to `AWAITING_APPROVAL`, then call `resume_after_hitl` with a signed token to advance.
4. Smoke the idempotency story: kill the worker mid-step (or just rerun `run_advancer` on a COMPLETED run) → no double side effect.

To start M8 from a cold context:
1. **Frontend canvas** — React Flow (or DnD-kit fallback) at `/[workspace]/automations/` with node palette (trigger, action, delay, branch, approval, end), node config drawer (right-side panel), connection validation, autosave to draft, publish-as-version flow.
2. **Backend** — extend `apps.automations` with `AutomationVersion` table (or version column on Automation) so publish creates immutable graph snapshots; running automations always reference a version. Add DRF serializers + `/api/automations/{id}/versions/` endpoint.
3. **Describe-in-English** — Claude prompt `automations.graph_from_nl.v1` taking a description + schema docs (entities + custom fields) returning a graph JSON. Streams into the canvas with a "review before save" gate.
4. **Run inspector UI** — surface AutomationStepRun rows (already in Django admin) into a per-run web page with step input/output/cost/latency + retry/cancel.
5. **Tests** — TC-29..TC-32 (publish a workflow, edit + republish, NL-to-graph happy path, cancel a stuck run).

Open `§14.1` items still defer-able. M11 (AI) needs token budget config; M10 (Gmail) needs GCP Pub/Sub topic + verified domain (~1 day setup).

## Revision log

- **2026-05** — initial commit `5375384`. PLAN.md rev 2 (Celery substitute, DO App Platform, flat monorepo). PRD / TESTING / ROADMAP added. M0 phase 1 scaffolded.
- **2026-05** — `0090063` added CLAUDE.md + MEMORY.md (this file) for durable repo-level context.
- **2026-05** — `dd2a003` scaffolded M0 phase 2a: `frontend-web/` (Next.js 15 + `/brand` token-demo route) and the three suite placeholders (`crunch-web`, `design-web`, `director-web`).
- **2026-05** — `d48c5ed` completed M0: Django backend (Celery + Procfile + Dockerfile + docker-compose + `apps.health` for liveness/readiness), `frontend-ios/` (xcodegen + SwiftUI placeholder with brand-token parity), GitHub Actions CI workflow. M0 done.
- **2026-05** — `268922c` updated MEMORY.md to mark M0 complete + add the M1 cold-context pickup guide.
- **2026-05** — `4ed442e` completed M1: `apps/users` (email-based custom User, hand-authored 0001 migration, UserAdmin, serializers), allauth + dj-rest-auth + SimpleJWT wired at `/api/auth/*`, public OpenAPI schema, real `openapi-typescript` codegen, conftest.py forcing Celery eager + locmem email in tests, signup/login/me + Celery + schema-served pytest coverage, prod settings tightening JWT cookies + ACCOUNT_DEFAULT_HTTP_PROTOCOL=https. M1 done.
- **2026-05** — `11b785f` updated MEMORY.md to mark M1 complete + add the M2 cold-context pickup guide.
- **2026-05** — `d9cc5ec` completed M2 backend: `apps/workspaces` with Workspace + Membership + Role + Invitation models, hand-authored 0001 migration, IsWorkspace{Member|Owner|Admin|Manager} permission classes, WorkspaceJWTAuthentication that resolves active workspace via X-Workspace-Id header, invite flow with Resend magic-link template, public + authenticated accept endpoints, comprehensive pytest coverage (workspace creation, invite + accept round-trip, cross-workspace 403, wrong-email 403, invalid-header 403). Settings switched to the workspace-aware auth class.
- **2026-05** — `5ee2c33` completed M2 frontend: `@offside/auth-utils` real implementation, `frontend-web/lib/api.ts` (TanStack Query v5 hooks), `lib/contexts.tsx`, `app/providers.tsx`, pages for /login, /signup, /onboarding, /accept-invite/[token], /[workspace]/{layout,page}, and a WorkspaceSwitcher. Path-segment routing locked. M2 done — TC-6/7/9 deferred to M3.
- **2026-05** — `96ff3fd` updated MEMORY.md to mark M2 complete + add M3 cold-context guide.
- **2026-05** — pushed all commits through `96ff3fd` to `origin/main` (10 commits backed up).
- **2026-05** — `b4fdaa7` completed M3: AppShell (Sidebar + TopBar with ⌘K hint) wraps the workspace route group, cmdk-powered CommandPalette with brand styling, useKeyboardShortcut hook (Cmd-K / "/" / Esc, input-aware). Settings page closes M2 deferrals (TC-6 role PATCH + TC-9 owner archive) with six new backend tests. cmdk@^1.0.4 added.
- **2026-05** — `36884a9` updated MEMORY.md to mark M3 complete + add M4 cold-context guide.
- **2026-05** — pushed M3 + MEMORY to `origin/main`.
- **2026-05** — `13a85ce` completed M4 backend: apps/companies + apps/contacts + apps/custom_fields with workspace-scoped models, JSONB custom columns, hand-authored 0001 migrations, IsWorkspaceManager gating writes, filter DSL v0 (JSON → Django Q with custom-field path resolution), 14 new tests covering CRUD + filter DSL + custom field defs + isolation.
- **2026-05** — `41b14ce` completed M4 frontend (excl. CSV import): TanStack Query hooks for contacts/companies/custom-field-defs, list + new + detail pages for both records, CustomFieldsPanel rendering typed inputs (text/number/select/date/etc) per CustomFieldDef, /[workspace]/settings/custom-fields/ admin UI. Sidebar Contacts + Companies links flipped from comingSoon placeholders to live routes. CommandPalette gains Contacts / Companies / Custom fields under Navigate.
- **2026-05** — pushed M4 backend + frontend to `origin/main`.
- **2026-05** — `b34ebec` completed M4 (last piece): apps/imports with ImportRun model (workspace + entity_type + raw_content + mapping + status counts + errors[]), heuristic header→field mapper, Celery task that streams CSV row-by-row, multipart /upload + /commit endpoints, ImportWizard component (upload → mapping review → progress polling at 1.5s) routed at /[workspace]/{contacts,companies}/import/. authFetch grew FormData support. 7 new backend tests. M4 done.
- **2026-05** — `03c692b` updated MEMORY.md to mark M4 complete + add M5 cold-context guide.
- **2026-05** — `12b53e9` completed M5 phase 1: apps/deals with Pipeline (stages JSONB) + Deal (FK pipeline + FK contact + FK company + value_cents + currency + expected_close + stage_id slug) + filter DSL reuse. WorkspaceScopedManager + IsWorkspaceManager gating writes.
- **2026-05** — `66ab096` completed M5 phase 2: apps/tasks (polymorphic related_type/related_id enum + ID pattern, NOT GenericForeignKey; status/priority enums; completed_at auto-stamp), apps/notes (Markdown body + 24h edit window + audit log on edits past that), apps/activities (append-only Activity rows + signal handlers on Contact/Company/Deal save firing activity events including DEAL_STAGE_CHANGED), shared RelatedType/ActivityKind/ActorKind enums in apps.activities.types. 17 new backend tests.
- **2026-05** — `9254b8d` updated MEMORY.md to reflect M5 backend complete (frontend pending).
- **2026-05** — `f428a47` completed M5 frontend: /[workspace]/deals/ DnD-kit kanban with optimistic stage_id PATCH on drag, deal new + detail pages, ActivityFeed + TasksTab + NotesTab reusable components integrated on contact + company + deal detail (replacing M4's "Coming in M5" stub). Sidebar Deals live; cmd-K reaches Deals. M5 done.
- **2026-05** — `c3507b1` updated MEMORY.md to mark M5 fully complete + add M6 cold-context guide.
- **2026-05** — `6d33a60` completed M6: SwiftUI iOS client. KeychainStore (SecItem wrapper for JWT persistence), AuthStore (`@Observable` with `.unknown/.signedOut/.needsWorkspace/.ready(workspace)` state + Keychain bootstrap on launch), APIClient singleton (mirrors authFetch — Bearer + X-Workspace-Id + retry-on-401 with refresh; baseURL via Info.plist's OffsideApiBaseUrl + localhost ATS exception in Project.yml). ContentView routes to LoginView / WorkspacePickerView / MainTabView; MainTabView has Contacts/Companies/Deals/More tabs with `@Observable` list models, NavigationStack push to detail views, pull-to-refresh, ErrorBanner overlay, brand-correct StatusPill / Eyebrow / EmptyStateView components. Deal rows resolve stage_id → label against workspace pipelines. Editing, custom-fields panel, tasks/notes/activity feeds, push notifications, and OpenAPI Swift codegen explicitly deferred (M13 push, codegen is a follow-up). M6 done.
- **2026-05** — `eeef2cb` updated MEMORY.md to mark M6 complete + add M7 cold-context guide.
- **2026-05** — `e69dfa3` completed M7: apps/automations ships the durable workflow state machine. Models: Automation + AutomationRun + AutomationStepRun + HitlRequest + AgentPolicy with status/run-state enums and the load-bearing `idempotency_key` unique constraint on AutomationStepRun. graph.py defines the JSON schema (action / delay / approval / branch / wait_for_event / end), template resolution (`{{ a.b.c }}` against state_snapshot), branch-condition evaluation. actions.py is the @register-decorated dispatcher with built-ins (noop, log, crm.create_contact, crm.move_deal_stage). tasks.py owns run_advancer (SELECT FOR UPDATE on the run row, idempotency-key short-circuit on replay, tail-recursive re-enqueue) + wake_up_sweep + resume_after_hitl. hitl.py wraps PyJWT for purpose-claim'd approval tokens with 7-day default TTL. Django admin gets a Run Inspector with inline AutomationStepRun rows. 14 new tests including the load-bearing replay-doesn't-double-create-contact (TC-34 chaos slice) + wake-up sweep round-trip + approval routing. CELERY_BEAT_SCHEDULE documents the wake_up_sweep entry pending a PeriodicTask data migration. M7 done.
- **2026-05** — added `[✅]/[🏗️]/[☑️]` status checkboxes across every epic / user story / engineering task / acceptance criterion in ROADMAP.md and across every FR / NFR / POST + user story + acceptance criterion in PRD.md. Each FR carries a "Roadmap mapping" line pointing at the milestone(s) shipping it. PRD bumped to v2 / ROADMAP gets a Revision 2 entry. CLAUDE.md gains a "Current milestone progress" section + the legend reference. MEMORY.md (this file) bumped to point at M8 as next. Documentation now visibly consistent with implementation status across the four docs.

---

*Update this file when state changes. Treat the "Current state" section as the authoritative pointer for "where are we right now."*
