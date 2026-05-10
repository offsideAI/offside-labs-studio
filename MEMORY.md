# MEMORY.md

> Running record of project state, locked decisions, and watch-outs. Companion to [PLAN.md](./PLAN.md) / [PRD.md](./PRD.md) / [TESTING.md](./TESTING.md) / [ROADMAP.md](./ROADMAP.md) — but **more living**. Update as state changes.

## Current state (2026-05)

- **Branch:** `main`. Local is **1 commit ahead of `origin/main`** (M5 frontend `f428a47`); everything through `9254b8d` is on origin.
- **Latest commits (newest first):**
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
  - **M6 — pending (next).** iOS shell + auth + read-only views. Maps to TC-68, TC-71, TC-88. Needs APNs key (placeholder bundle ID is `ai.offside.crm`).
  - **M7–M15 — pending.** Per [ROADMAP.md](./ROADMAP.md).

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

M4 is complete. **Next milestone is M5 (deals + pipelines + tasks + notes + activities).**

Verify M4 locally first:
1. `pnpm install` (no new JS deps in CSV import). `pnpm backend:up` + `pnpm backend:migrate` (runs 4 new migrations: contacts/companies/custom_fields/imports) + `pnpm backend:test` (44 backend tests; 14 new from M4).
2. `pnpm dev` → /{slug}/contacts → "+ New contact" → fill standard + custom fields → save → land on detail page → "Edit" → modify → "Archive". Same for /{slug}/companies. Detail pages show linked records (TC-13).
3. /{slug}/settings/custom-fields → add a `lead_score` number field on contacts. Re-open a contact to see the field on the form.
4. /{slug}/contacts/import → upload a CSV with `First Name,Last Name,Email` headers → review heuristic mapping → commit → progress polls every 1.5s → done. Errors show inline.

To start M5 from a cold context:
1. **`apps.deals`** — Deal + Pipeline + Stage models. Pipeline holds an ordered JSONB stages array. Deal has FK pipeline + FK contact + FK company + value_cents + currency + expected_close.
2. **`apps.tasks`** — Task with polymorphic `(related_type, related_id)` (small enum + ID, NOT GenericForeignKey). Status, priority, due_at, owner FK.
3. **`apps.notes`** — Markdown body with 24h edit window; audit row created on edits beyond that.
4. **`apps.activities`** — append-only event log. Signal hooks on Contact/Company/Deal/Task save fire activity rows. Polymorphic `(related_type, related_id)`.
5. **Frontend** — kanban view (DnD-kit) for /{slug}/deals; deal/task/note detail pages; real activity feed on every record (replacing M4's "Coming in M5" stub).
6. **Tests** — TC-15..TC-21.

Open `§14.1` items still defer-able. M6 (iOS) needs APNs key; M11 (AI) needs token budget config.

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

---

*Update this file when state changes. Treat the "Current state" section as the authoritative pointer for "where are we right now."*
