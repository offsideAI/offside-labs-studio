# MEMORY.md

> Running record of project state, locked decisions, and watch-outs. Companion to [PLAN.md](./PLAN.md) / [PRD.md](./PRD.md) / [TESTING.md](./TESTING.md) / [ROADMAP.md](./ROADMAP.md) — but **more living**. Update as state changes.

## Product positioning (locked, 2026-05)

**OffsideStudio — Agent Marketplace** is the default selling proposition. The product leads with two hero surfaces:

- **★★ Agents Marketplace** (FR-26 / M9.S4) — curated catalog of pre-built workflow agents. One-click install creates an editable, immediately-runnable workflow in the workspace. This is the headline of the product.
- **★ Agent Design Studio** (FR-12 / M8 — formerly "Workflow node-graph editor") — visual canvas + run inspector + describe-in-English authoring. Where every installed agent opens for customization.

CRM record views (contacts/companies/deals/tasks/notes/activities) are the underlying data layer the agents act on, not the headline. Primary navigation should put Marketplace + Studio above the CRM record entries.

## Current state (2026-05)

- **Branch:** `main`. Up to date with `origin/main` through `ba13d83`. M0–M7 + the **M8 backend slice** are committed and pushed (`814b839` + `ba13d83`). Everything else listed below — **M8 frontend canvas + M8.S3 describe-in-English + M9 triggers + M9 actions + M9.S4 Agents Marketplace (backend + frontend + 15-agent catalog incl. the hero) + demo workspace seed + DEMO.md + repositioning to OffsideStudio — Agent Marketplace + frontend copy sweep** — is **shipped locally, awaiting commit**.
- **Product positioning (locked, 2026-05):** *OffsideStudio — Agent Marketplace* is the default selling proposition. Two hero surfaces lead the UX: **★★ Agent Marketplace** (FR-26 / M9.S4) and **★ Agent Design Studio** (FR-12 / M8 — renamed from "Workflow node-graph editor"). CRM record views (contacts / companies / deals / tasks / notes) are the data layer agents act on, not the headline. Sidebar reorder puts Marketplace + Studio above CRM records.
- **Demo readiness (2026-05):** 5-min stage demo scripted in `DEMO.md`. Hero agent — *Ecommerce Conversion Funnel Optimizer* (slug `ecommerce-conversion-funnel-optimizer`) — is a 10-node manual-triggered workflow: init log → marketing campaign launch → AEO content seed → ad sync → landing-page generation → create demo-funnel company → email welcome task → cart recovery task → payment confirmation task → deployment-summary note. Demo opener is "install the hero agent live."
- **Latest commits (newest first):**
  - `ba13d83` Updated ROADMAP.md (Revision 3 — M8 backend slice annotations)
  - `814b839` M8 backend: AutomationVersion snapshots + automations DRF + run inspector API
  - `e86b6a0` Sync docs: add [✅]/[🏗️]/[☑️] checkboxes across PRD + ROADMAP
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
  - **M8 — Agent Design Studio v1 — all 3 user stories shipped locally** (backend committed via `814b839`; frontend awaiting commit). M8.S1: React Flow canvas + node palette + per-node config drawer + drag-from-palette + validation overlay. M8.S2: AutomationVersion immutable snapshots + 300ms debounced autosave + Publish gated on validateGraph issues + Versions slide-in panel + per-run Run Inspector at `/[workspace]/automations/[id]/runs/[runId]/` showing input/output/cost/latency/idempotency_key with manual Refresh + Cancel button + 3s live polling. M8.S3: apps/ai Django app with `AICall` telemetry model + Anthropic SDK wrapper + `automations.author_from_nl.v1` prompt using Claude tool_use + `POST /api/automations/{id}/generate_from_nl/` endpoint + frontend Describe panel with Apply/Discard review gate. **35 backend tests + 9 ai tests shipped.** Remaining: HITL HTTP decide endpoint, undo/redo, full type-mismatch validator.
  - **M9 — Workflow engine completeness + Agents Marketplace — partially shipped locally.** M9.S1: 4 of 5 v1 trigger types — record (signal-handler dispatch via transaction.on_commit), webhook (HMAC SHA-256, public POST /api/webhooks/{token}/), schedule (cron via celery.schedules.crontab + Beat sweep, no-backlog semantics), form (public POST /api/forms/{token}/submit/ with rate limiting + 429 + Retry-After). 34 tests. AI-condition trigger deferred to M11. M9.S2: action expansion to 13 registered actions — `crm.http.request` (auth presets none/bearer/basic/custom-header, 256KB body cap, basic SSRF guard), `crm.loop` (per-item `{{ item.* }}` / `{{ index }}` templating, on_error continue/abort, 5000 hard cap, self-nest guard), CRM mutates across the M5 entities (`crm.update_contact`, `crm.create_company` + `crm.update_company`, `crm.create_deal` validating stage_id against pipeline, `crm.update_deal`, `crm.create_task` validating related_type allowlist, `crm.create_note`). 46 tests. M9.S3 Slack: pending. **M9.S4 — Agents Marketplace v1 ★★ hero — fully shipped locally**: `apps/marketplace` Django app (MarketplaceAgent workspace-agnostic catalog + WorkspaceAgentInstall audit, hand-authored migrations 0001 + 0002 with 4 new ecommerce-lifecycle category values), `MarketplaceAgentViewSet` with public AllowAny browse + manager-gated install (atomic snapshot into Automation + AutomationVersion + bumps install_count, `__INSTALLER__` sentinel resolution), wired at `/api/marketplace/`. Frontend grid + detail (read-only canvas preview) + Install button + sidebar repositioning (Marketplace + Studio above CRM records) + `/automations` empty-state pitching the Marketplace. 9 tests covering TC-92..TC-94. **15-agent catalog seeded** via `tools/seeds/marketplace.py` — the hero *Ecommerce Conversion Funnel Optimizer* (10 nodes) plus 4 originals + 10 ecommerce-lifecycle agents (Lead from form, Welcome series day 0, Abandoned cart recovery, Order received, Shipping dispatched, Payment success, Failed payment retry, Refund request handler, Post-purchase review request, Repeat-purchase nudge). M7 runtime tweak: `run_advancer` now seeds `state_snapshot.trigger = trigger_payload` on PENDING→RUNNING so `{{ trigger.* }}` templates resolve.
  - **Demo prep — shipped locally.** `tools/seeds/demo_workspace.py` creates an idempotent demo workspace (slug `acme-demo`, owner `demo@offside.ai` / `DemoOnly123!`) with default pipeline + 8 companies + 20 contacts + 12 deals + 5 tasks + 3 notes. `DEMO.md` presenter script with setup checklist + 5-min click-by-click + common-issues table + pre-stage hash check + condensed narrative arc. Frontend copy sweep done: `Offside CRM` → `OffsideStudio` across layout.tsx / page.tsx / signup / login / accept-invite / onboarding / top-bar; `workflow` / `Automations` → `agent` / `Agent Design Studio` in user-facing copy.
  - **M10–M15 — pending.** Per [ROADMAP.md](./ROADMAP.md).

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

## Demo-day watch-outs (2026-05)

- **Live trigger on stage:** Step 5 of `DEMO.md` ("create a contact → see the agent fire") depends on the Celery worker being up. If you see no run in the editor footer within 3s of creating a contact, the worker is down — re-run `pnpm backend:up` and confirm `worker` is `Up` in `docker compose ps`.
- **`__INSTALLER__` sentinel** in seed graphs must be resolved to the installer's user id on install. If a run fails because `created_by_id == "__INSTALLER__"` (literal string), the install endpoint's `_resolve_installer_sentinels` mis-fired — re-install the agent.
- **Hero agent `n6` (Create funnel company record)** uses `name: "Acme Demo Funnel · {{ n2.status_code }}"`. The `200` interpolation is intentional theatrics — proves step chaining is real to the audience. If httpbin.org is unreachable, n2 will fail and the rest of the chain skips; have a screenshot ready.
- **`ANTHROPIC_API_KEY` for Describe-in-English** (Step 5 bonus of demo) is optional — if missing or rate-limited, skip Step 5 cleanly with the verbal-only mention.
- **Demo workspace seed creates user `demo@offside.ai` / `DemoOnly123!`** — those creds are literal in `tools/seeds/demo_workspace.py` and DEMO.md. Don't change them without updating both.

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

**M8 + M9.S1 + M9.S2 + M9.S4 + demo prep all shipped locally — `main` is at `ba13d83` (M8 backend slice only). ~19 slices of work are uncommitted in the working tree, ready for a single commit + push.**

**Critical-path remaining for conference demo:**

1. **Smoke pass** (~4h, requires toolchain):
   ```bash
   pnpm backend:up
   pnpm backend:migrate                     # applies marketplace 0001 + 0002 + ai 0001 + automations 0002..0005
   python -m tools.seeds.marketplace        # seeds the 15-agent catalog (incl. the hero)
   python -m tools.seeds.demo_workspace     # seeds demo@offside.ai + acme-demo workspace + CRM data
   pnpm backend:test                        # confirm all backend tests green
   pnpm dev                                 # web at :3000
   ```
   Walk the `DEMO.md` 5-min narrative end-to-end. Hero-agent run must complete cleanly with all 10 step rows visible in the Inspector.
2. **Commit + push** the pile (subject for a separate prompt to me — I won't push without explicit instruction).
3. **Deploy to production URLs** — Django → DO App Platform; web → Vercel. `crm-api.offside.ai` + `app.offside.ai`.

**Nice-to-have if time:**
- **M9.S3 Slack OAuth** (~2 days) — promotes the hero's `crm.http.request` placeholders to real Slack posts. Skip if time-tight; httpbin.org placeholders demo convincingly.
- **M8 HITL HTTP decide endpoint** (~0.5 days) — needed only if a marketplace agent uses HITL approval nodes during the demo (none currently do).
- **M9.S1 AI-condition trigger** — defers to M11 per ROADMAP.

**To run the demo from a cold context** (full workflow once toolchain is up):
1. Follow the smoke-pass commands above.
2. Open `DEMO.md`. Walk the 5-step narrative: frame → install the 🚀 hero agent → run live → switch to Companies to see records → bonus describe-in-English → close.
3. Pre-stage hash check (in DEMO.md §"Pre-stage hash check") returns: agents=15, hero=True, contacts=20, companies=8, JWT issues correctly.

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
