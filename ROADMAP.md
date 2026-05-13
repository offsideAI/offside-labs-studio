# OffsideStudio — Agent Marketplace — Roadmap (ROADMAP.md)

> Companion to [PRD.md](./PRD.md) and [PLAN.md](./PLAN.md). Each **phase maps 1:1 to an epic.** Inside an epic, work is broken into user stories (the "what" from a user's view) and engineering tasks (the "how"). Acceptance criteria match the milestone demo defined in PLAN.md §13. Cross-references to PRD `FR-N` / `NFR-N` and TESTING `TC-N` are noted on each phase.
>
> **★★ Hero surface — FR-26 — Agents Marketplace** (M9.S4). **★ Hero surface — FR-12 — Agent Design Studio** (M8). All other phases are foundational for these two surfaces.

**Status:** Product repositioned around **OffsideStudio — Agent Marketplace** (default selling proposition). M0–M7 shipped + pushed to `origin/main`. **M8 — ★ Agent Design Studio v1** — all three user stories (S1 + S2 + S3) shipped locally. M9 — 4 of 5 v1 trigger types + 3 action-expansion phases shipped (13 registered actions); **M9.S4 — ★★ Agents Marketplace v1 (FR-26)** — backend shipped, frontend pending — **demo-critical, hero surface**. Lingering: AI-condition trigger, Slack OAuth/action, run-inspector retry counts, M8 HITL HTTP decide endpoint + undo/redo + TC-29..TC-32 frontend smoke-tests.
**Owner:** Offside Labs.
**Last revised:** 2026-05.

---

## Status legend

| Symbol | Meaning | Used on |
|---|---|---|
| `[✅]` | Implemented and on `main` (or shipped locally in a tagged Revision N block at the bottom of this file, awaiting commit). | Phase headers, user stories, engineering tasks, acceptance criteria. |
| `[🏗️]` | Partially implemented — some pieces done, others pending. Always paired with an inline note describing what shipped vs what's left. | Same as above. |
| `[☑️]` | Pending — not started yet, or scoped but not implemented. | Same as above. |

**Granularity.** Phase headers carry a single rollup status; stories, engineering tasks, and acceptance criteria each get their own checkbox so half-done milestones (deferred items punted to later milestones) stay honest. A phase is `[✅]` only when every story under it is `[✅]`.

**Cross-references.** Stable inline IDs (`M2.S3`, `FR-12`, `TC-64`, `NFR-5`) link out to PRD.md and TESTING.md. Don't reuse a retired ID — append, never recycle.

**Revision blocks.** Material slices added between commits get a `### Revision N — YYYY-MM — <summary>` block in the "Status updates" section at the bottom, with a file-by-file breakdown. Revision blocks are append-only.

---

## Conventions

- **Phase / Epic ID:** `M-N` for MVP, `POST-N` for post-MVP placeholders.
- **Stories:** "As a [persona], I [action] so that [outcome]." Each story has a stable inline ID like `M2.S3` referenced in PR descriptions and TESTING.md cases.
- **Tasks:** engineering breakdown. Not exhaustive — focused on the load-bearing pieces. Routine work (lint, format, test scaffolding) is implicit.
- **Estimate:** working days for one focused senior engineer. Calendar time is roughly 1.7× this with normal coordination overhead.

Color discipline reminder: every UI surface added in any phase MUST consume `packages/ui` tokens. No bespoke brand colors. (NFR-5)

---

## MVP

### `[✅]` Phase M0 — Repo scaffold (Epic: Repo Foundations)
*Status:* complete · *Estimate:* 3 days · *Depends on:* — · *Covers:* infra · *Tests:* (smoke build only) · *Commits:* `5375384`, `dd2a003`, `d48c5ed`

**User stories**
- `[✅]` M0.S1 — As an engineer, I can clone the repo and run `pnpm install && docker compose up && pnpm dev` and have all surfaces healthy locally.
- `[✅]` M0.S2 — As a designer, I can open `/brand` in any web app and see the live brand-token demo.
- `[✅]` M0.S3 — As an engineer, I can `pnpm ios:gen` and open the Xcode project that builds.

**Engineering tasks**
- `[✅]` pnpm workspace + Turborepo wiring; root configs (`.gitignore`, `.editorconfig`, prettier, turbo.json).
- `[✅]` `packages/config` — shared tsconfig + Tailwind preset + Next base config.
- `[✅]` `packages/ui` — brand tokens CSS adopted verbatim from offside.ai marketing site; Button / Card / Eyebrow / Hairline / StatusPill primitives.
- `[✅]` `packages/{ai, auth-utils, workflows-sdk, api-client}` — typed scaffolds with stub exports.
- `[✅]` `tools/openapi/codegen.mjs` — placeholder until M1's drf-spectacular schema is real.
- `[✅]` `frontend-web/` — Next.js 15 app shell, `globals.css` importing tokens, `/brand` token-demo route, `next/font/google` for Roboto + JetBrains Mono.
- `[✅]` `crunch-web/`, `design-web/`, `director-web/` — 10-line shells importing `@offside/ui`.
- `[✅]` `backend/` — fresh Django 4.2 project, settings split (base/dev/prod), Celery wiring (`celery.py` + `app.autodiscover_tasks`), `Procfile` (web/worker/beat), `Dockerfile`, `docker-compose.yml` (postgres + redis + django + worker + beat).
- `[✅]` `frontend-ios/` — `Project.yml` (xcodegen), `OffsideCRMApp.swift`, `ContentView.swift`, README with Xcode steps.
- `[✅]` `.github/workflows/ci.yml` — lint + typecheck + Django tests + OpenAPI drift check.

**Acceptance criteria**
- `[✅]` `pnpm dev` boots all 4 web apps.
- `[✅]` `pnpm backend:up` boots Django + Postgres + Redis + Celery.
- `[✅]` Visiting `/brand` on each app renders the tokens demo without bespoke colors.
- `[✅]` `pnpm ios:gen && open frontend-ios/OffsideCRM.xcodeproj` opens an app that builds.

---

### `[✅]` Phase M1 — Backend foundation (Epic: Auth & API Plumbing)
*Status:* complete · *Estimate:* 3 days · *Depends on:* M0 · *Covers:* FR-2 (full), NFR-3 · *Tests:* TC-1, TC-2, TC-3, TC-4 · *Commits:* `4ed442e`

**User stories**
- `[✅]` M1.S1 — As a new user, I can sign up with email + password and receive a verification email.
- `[✅]` M1.S2 — As an engineer, I can hit `/api/schema/` and get a complete OpenAPI 3.1 document.
- `[✅]` M1.S3 — As an engineer, I can fire off a Celery `ping` task and see it executed by a worker.

**Engineering tasks**
- `[✅]` Postgres 16 + pgvector extension enabled; Django connects via `DATABASE_URL`.
- `[✅]` `apps/users` Django app — custom `User` (email-based, no username), allauth + dj-rest-auth wiring, SimpleJWT (access 1d, refresh 14d, blacklist on logout).
- `[✅]` Email backend wired to **Resend** via SMTP; verification + password-reset templates.
- `[✅]` `drf-spectacular` for OpenAPI; `/api/schema/` + `/api/docs/` (Swagger).
- `[✅]` `offside_crm/celery.py` configured; ping task lands; Beat schedule loader pulls from a future `automations` app.
- `[✅]` Health endpoints `/api/health/live/`, `/api/health/ready/` (DB + Redis check).
- `[✅]` `tools/openapi/codegen.mjs` regenerates `@offside/api-client/src/generated/`.

**Acceptance criteria**
- `[✅]` `POST /api/auth/registration/` → email verification → login → `/api/auth/user/` returns the user.
- `[✅]` `make celery-ping` returns from worker (smoke test passes).
- `[✅]` `pnpm codegen:openapi` succeeds.

---

### `[✅]` Phase M2 — Workspaces + multi-tenancy + invite flow (Epic: Tenancy)
*Status:* complete · *Estimate:* 4 days · *Depends on:* M1 · *Covers:* FR-1, FR-24 partial · *Tests:* TC-5, TC-6, TC-7, TC-8 · *Commits:* `d9cc5ec`, `5ee2c33`

**User stories**
- `[✅]` M2.S1 — As a user, I can create a workspace from a sign-up landing.
- `[✅]` M2.S2 — As an owner, I can invite a teammate via Resend magic-link with a chosen role.
- `[✅]` M2.S3 — As a multi-workspace user, I can switch workspaces in ≤2 keystrokes.
- `[✅]` M2.S4 — As a backend engineer, I can trust that workspace isolation is enforced at the ORM layer and audited by tests.

**Engineering tasks**
- `[✅]` `apps/workspaces` Django app — `Workspace`, `Membership`, `Role` enum (`owner|admin|manager|rep|read_only`).
- `[✅]` `WorkspaceScopedManager` Django ORM manager (rather than a JWT claim, the active workspace travels as `X-Workspace-Id` — zero-token-rotation switching).
- `[✅]` Custom DRF permission classes (`IsWorkspaceMember`, `IsWorkspaceAdmin`, etc.) checking `Membership.role` against per-view requirements.
- `[✅]` `WorkspaceJWTAuthentication` — wraps SimpleJWT and validates the `X-Workspace-Id` header against active memberships.
- `[✅]` Invite flow — `Invitation` model with single-use UUID token, Resend HTML email template, public detail + authenticated `accept` endpoints.
- `[✅]` `packages/auth-utils` (TS) — real `authFetch` with refresh-on-401 + workspace-header injection.
- `[✅]` Web — basic workspace switcher (cmd-K integration polished in M3).

**Acceptance criteria**
- `[✅]` TC-5, TC-7, TC-8 pass (invite, switch, cross-workspace 403).
- `[✅]` Cross-workspace API calls return 403/404 (no leakage).
- `[✅]` TC-6 (role promotion) and TC-9 (workspace archive) deferred to M3 settings page — implemented there.

---

### `[✅]` Phase M3 — Web shell + cmd palette + keyboard nav (Epic: Web App Shell)
*Status:* complete · *Estimate:* 3 days · *Depends on:* M2 · *Covers:* NFR-1, NFR-2, foundation for FR-19 · *Tests:* TC-7, TC-55, TC-75–TC-79 · *Commits:* `b4fdaa7`

**User stories**
- `[✅]` M3.S1 — As any user, I can navigate the entire app with keyboard alone.
- `[✅]` M3.S2 — As a power user, I can press `Cmd+K` and reach any record / page in seconds.
- `[🏗️]` M3.S3 — As a screen-reader user, I can complete the core flows announced correctly. *(Manual screen-reader pass deferred to M15 polish.)*

**Engineering tasks**
- `[✅]` AppShell layout — sidebar (collapsible), top bar (workspace switcher + user menu + global search trigger), main, slot for sub-nav.
- `[✅]` Cmd-K palette skeleton — fuzzy command match via `cmdk@^1.0.4`, brand-tan selected state, workspace + nav search.
- `[✅]` Keyboard nav primitives — `useKeyboardShortcut` hook handles Cmd-K toggle, `/` open, `Esc` close. (`j/k` row nav and `n` create deferred to M4 lists.)
- `[✅]` Focus management — focus-trap inside the cmdk Dialog, focus-restore on close.
- `[✅]` Skip link wired in app/layout.tsx; visible on first Tab.
- `[☑️]` Axe-clean smoke pass on shell — formalized as a CI gate in M15 polish.
- `[✅]` Settings page closes M2 deferrals: TC-6 (role promotion via PATCH) + TC-9 (owner archive with slug-confirmation).
- `[☑️]` Marketing-grade `/login`, `/signup` chrome polished — punted to M15.

**Acceptance criteria**
- `[✅]` TC-75 (keyboard walk), TC-76 (reduced motion), TC-77 (skip link) pass.
- `[☑️]` TC-78 (axe-clean) — manual passes; CI gate in M15.
- `[☑️]` TC-79 (screen reader pass) — deferred to M15.

---

### `[✅]` Phase M4 — Contacts + Companies + Custom fields + CSV import (Epic: Core Records)
*Status:* complete · *Estimate:* 4 days · *Depends on:* M3 · *Covers:* FR-3, FR-4, FR-8, FR-20 (CSV slice) · *Tests:* TC-10–TC-14, TC-22–TC-24, TC-58, TC-84 · *Commits:* `13a85ce`, `41b14ce`, `b34ebec`

**User stories**
- `[✅]` M4.S1 — As a rep, I can create / edit / archive contacts and companies.
- `[✅]` M4.S2 — As a rep, I can import 1k–5k contacts from CSV in ~5 minutes with heuristic column mapping (Claude-powered mapping deferred to M11).
- `[✅]` M4.S3 — As an admin, I can define custom fields on contacts/companies (text/long_text/number/select/multi_select/date/datetime/boolean/url/email/phone/relation).
- `[✅]` M4.S4 — As a rep, I can filter the contacts list by any standard or custom field via the JSON DSL.

**Engineering tasks**
- `[✅]` `apps/contacts`, `apps/companies` Django — workspace-scoped models with JSONB `custom` column, indexes on hot keys.
- `[✅]` `apps/custom_fields` — `CustomFieldDef` model with EntityType + FieldType enums + admin CRUD endpoints.
- `[✅]` Filter DSL v0 — JSON-encoded operator grammar (`{"and":[{"field":"custom.lead_score","op":"gt","value":70}]}`); evaluator in `apps/contacts/filters.py`, reused by Companies + Deals.
- `[✅]` List view (web) — paginated table with custom field columns + click-through to detail.
- `[☑️]` Virtualized list (`@tanstack/react-virtual`) — deferred until lists actually demand it post-MVP.
- `[✅]` Detail view (web) — header, custom-fields panel; activity-feed stub replaced with real feed in M5.
- `[✅]` CSV import — `apps/imports` ImportRun model + Celery task + heuristic header→field mapper (Claude version is M11) + multipart upload + commit + progress polling wizard.

**Acceptance criteria**
- `[✅]` TC-10 (create contact), TC-11 (edit), TC-12 (archive), TC-13 (contact-company nav).
- `[🏗️]` TC-14 (bulk edit) — basic via filter + iterate; bulk-action UI deferred to M14 polish.
- `[✅]` TC-22 (define custom field), TC-23 (filter by custom), TC-24 (select with options).
- `[✅]` TC-58 (CSV import small slice — full 5k-row test in TESTING.md uses pytest's eager Celery; production load testing deferred).
- `[✅]` TC-84 (empty state CTA points at import).

---

### `[✅]` Phase M5 — Deals + Pipelines + Tasks + Notes + Activities (Epic: Pipeline & Records v2)
*Status:* complete · *Estimate:* 4 days · *Depends on:* M4 · *Covers:* FR-5, FR-6, FR-7 · *Tests:* TC-15–TC-21 · *Commits:* `12b53e9`, `66ab096`, `f428a47`

**User stories**
- `[✅]` M5.S1 — As a manager, I can define a pipeline with custom stages and assign deals to it.
- `[✅]` M5.S2 — As a rep, I can drag deals across stages on a kanban view.
- `[✅]` M5.S3 — As a rep, I can attach tasks and notes to any record (contact / company / deal).
- `[✅]` M5.S4 — As any user, I see a chronological activity feed on every record.

**Engineering tasks**
- `[✅]` `apps/deals` — `Deal`, `Pipeline` (stages as ordered JSONB array on Pipeline), `default_pipeline_stages` helper.
- `[✅]` `apps/tasks` — `Task` model with polymorphic `(related_type, related_id)` enum-based pattern (no GenericForeignKey).
- `[✅]` `apps/notes` — `Note` (Markdown body) + 24-hour edit window with audit `edit_log` JSONB beyond that.
- `[✅]` `apps/activities` — append-only `Activity` event log + signal hooks on Contact/Company/Deal save + `DEAL_STAGE_CHANGED` on stage_id `update_fields`.
- `[✅]` Web — DnD-kit kanban with optimistic `stage_id` PATCH on drop, deal new + detail pages, real `ActivityFeed` + `TasksTab` + `NotesTab` reusable components integrated on contact + company + deal detail.

**Acceptance criteria**
- `[✅]` TC-15 (pipeline + custom stages), TC-16 (create deal), TC-17 (drag stages), TC-18 (close deal).
- `[✅]` TC-19 (task on contact), TC-20 (overdue tan-text accent), TC-21 (Markdown note).

---

### `[✅]` Phase M6 — iOS shell + auth + read-only views (Epic: iOS Foundation)
*Status:* complete · *Estimate:* 5 days · *Depends on:* M5 · *Covers:* FR-23 (read-only slice), NFR-1 · *Tests:* TC-68, TC-71, TC-88 · *Commits:* `6d33a60`

**User stories**
- `[✅]` M6.S1 — As a rep, I can log in on iOS with my web credentials.
- `[✅]` M6.S2 — As a rep, I can browse contacts, companies, deals on iOS read-only. *(Tasks tab on iOS deferred to M13.)*
- `[☑️]` M6.S3 — As a rep, the app caches my last 50 visited records for offline read. *(Local SwiftData/JSON cache deferred — landing in a polish pass before M13.)*

**Engineering tasks**
- `[✅]` `frontend-ios` SwiftUI app — LoginView + JWT in Keychain (`KeychainStore`) + AuthStore (`@Observable`) state machine.
- `[✅]` Hand-rolled `APIClient` (URLSession + Codable + `convertFromSnakeCase`) mirroring `packages/auth-utils` authFetch — Bearer + X-Workspace-Id + retry-on-401.
- `[☑️]` OpenAPI Swift codegen (`tools/openapi/sync-ios.sh`) wired into Xcode build phase. *(Hand-rolled models in `Models.swift` for now; codegen is a follow-up commit.)*
- `[✅]` List + detail screens for Contact / Company / Deal with NavigationStack push.
- `[☑️]` Tasks tab on iOS — deferred to M13.
- `[☑️]` Local cache (SwiftData or simple JSON-file cache) for offline read of last 50 records.
- `[☑️]` APNs registration + token round-trip to backend. *(Deferred to M13 push notifications.)*
- `[✅]` Pull-to-refresh on every list.
- `[☑️]` Skeleton loading states. *(Inline spinner today; skeleton component lands in M15 polish.)*
- `[🏗️]` Offline banner + retry button. *(Basic `ErrorBanner` on transport failure exists; full offline-detection + queued-edits banner deferred.)*

**Acceptance criteria**
- `[✅]` TC-68 (cold start to "today" view) — initial brand-correct surface boots fast.
- `[✅]` TC-71 (pull-to-refresh) — works on every list view.
- `[🏗️]` TC-88 (offline cached data + retry) — retry button is in; cached read deferred.
- `[☑️]` App Store review checklist locally green — formalized at the M15 polish + TestFlight cycle.

---

### `[✅]` Phase M7 — Workflow runtime v0 (Epic: Durable Workflow Engine)
*Status:* complete · *Estimate:* 7 days · *Depends on:* M5 · *Covers:* FR-11 (foundation), NFR-7 · *Tests:* TC-33, TC-34, TC-39 · *Commits:* `e69dfa3`

**User stories**
- `[✅]` M7.S1 — As an engineer, I can author a workflow as JSON, persist it as `Automation`, and watch a `run_advancer` Celery task walk it durably.
- `[✅]` M7.S2 — As an admin, the run inspector in Django admin shows me every step's input / output / cost / latency.
- `[✅]` M7.S3 — As an SRE, when I kill a worker mid-step, the workflow recovers without duplicate side effects.

**Engineering tasks**
- `[✅]` `apps/automations` Django — `Automation`, `AutomationRun`, `AutomationStepRun`, `HitlRequest`, `AgentPolicy` models with status/run-state enums per PLAN §6.
- `[✅]` `automations.tasks.run_advancer(run_id)` Celery task — SELECT FOR UPDATE on the run row, execute next step, persist state, re-enqueue or park.
- `[✅]` Idempotency: action handlers short-circuit on cached output via the `(run_id, step_id, attempt)` unique-constrained `idempotency_key`.
- `[✅]` Beat task `wake_up_sweep` — finds runs with `resume_at <= now()`, re-enqueues advancers.
- `[☑️]` `wake_up_sweep` registered as a `PeriodicTask` row for `DatabaseScheduler` — currently in `CELERY_BEAT_SCHEDULE` for documentation; data migration to register the row pending (rolls forward to M15 polish).
- `[✅]` Action handler registry — `@actions.register("crm.create_contact")` decorators with built-ins (noop, log, crm.create_contact, crm.move_deal_stage).
- `[✅]` Run inspector view in Django admin — `AutomationRunAdmin` with inline `AutomationStepRun` rows showing input/output/idempotency_key.
- `[🏗️]` HITL primitive — `HitlRequest` row + signed JWT approval token are done; `/api/hitl/<token>/decide` HTTP endpoint pending in M7 phase 2 (workflow ViewSets/URLs).

**Acceptance criteria**
- `[✅]` TC-33 (delay parks run + advances), TC-34 (worker kill mid-step doesn't duplicate side effects via the chaos test `test_replay_does_not_double_create_contact`), TC-39 (basic retry path on transient failure).
- `[✅]` Programmatically created multi-step workflow with delay survives a worker kill mid-delay.

---

### `[🏗️]` Phase M8 — ★ Agent Design Studio v1 (Epic: Visual Authoring · hero surface)
*Status:* all three user stories shipped — only HITL HTTP decide endpoint, undo/redo, and TC-29..TC-32 frontend smoke-tests remain · *Estimate:* 7 days · *Depends on:* M7 · *Covers:* FR-12 (partial) · *Tests:* TC-29, TC-30, TC-31, TC-32

**User stories**
- `[✅]` M8.S1 — As an admin, I can build a workflow visually with React Flow. *Canvas at `/[workspace]/automations/[id]/` ships with @xyflow/react v12, draggable palette (action / branch / delay / approval / wait_for_event / end), custom brand-tokened node renderer with per-type source handles (`true`/`false`, `approve`/`reject`, `next`), drop-onto-canvas, set-as-start, delete, and inline validation overlay.*
- `[✅]` M8.S2 — As an admin, I can save drafts and publish versioned workflows. *End-to-end shipped. Backend: `AutomationVersion` snapshot model + `POST /automations/{id}/publish/` + `start_run` attaches the published version + `POST /automation-runs/{id}/cancel/`. Frontend: 300ms debounced autosave to draft, Publish button gated on `validateGraph` issues, status pill + `v{N}` header, slide-in Versions panel listing AutomationVersion rows (with `current` badge + frozen-graph JSON preview), and full per-run Inspector page surfacing step inputs/outputs/cost/idempotency_key with manual Refresh + Cancel-run button (light 3s polling while non-terminal).*
- `[✅]` M8.S3 — As an admin, I can describe a workflow in English and have Claude generate the node graph. *Backend: new `apps/ai` Django app with `AICall` telemetry model (workspace, prompt_name, model, status, tokens_in/out, cost_cents, latency_ms, optional run+step_id FK, error, metadata) — every LLM call writes a row whether it succeeds or fails. Prompt registry centered on `automations.author_from_nl.v1` which forces Claude tool_use against a `build_graph` JSONSchema so the model can't drift from the graph shape; client wrapper hardcodes per-Mtok pricing for Sonnet 4.6 / Opus 4.7 / Haiku 4.5 so cost rows aren't zero, and exposes `set_override_caller` so tests never hit the real API. `POST /api/automations/{id}/generate_from_nl/` returns a proposed graph WITHOUT saving (frontend reviews + PATCHes via the existing autosave path). Frontend: collapsible Describe panel between header and canvas — left has the textarea + Generate + three example prompts, right shows node count + tokens + latency + JSON preview with Apply / Discard buttons. 8 tests cover service happy path + AICall row, empty tool input + AIResponseError, bad graph shape, transport failure + error-row, prompt registry, and the DRF endpoint at 200/400/502.*

**Engineering tasks**
- `[🏗️]` M7 phase 2 prerequisite — DRF ViewSets for `/api/automations/` + `/api/automation-runs/` + `/api/automation-versions/` (CRUD, publish, versions, start_run, cancel) shipped with manager-gated writes and 18 tests. `/api/hitl/<token>/decide/` endpoint still pending — `hitl.py` service exists from M7 but is not yet wired to DRF.
- `[✅]` React Flow canvas — node palette (action / branch / delay / approval / wait_for_event / end). Custom `AutomationNodeView` with multi-handle source ports, dotted Bone background, hidden RF attribution, MiniMap + Controls, drop-from-palette via HTML5 drag.
- `[✅]` Node config drawer — per-node form driven by node type (action name + JSON input, delay seconds, approval summary + TTL, branch field/op/value, wait_for_event key) with a live JSON textarea that surfaces parse errors inline; Set-as-start + Delete; label editor.
- `[✅]` Save draft + publish flow — `frontend-web/lib/workflow-graph.ts` round-trips between `AutomationGraph` and React Flow nodes/edges (positions and label are editor-only keys carried through the JSON); 300ms debounced PATCH on every change with a hash gate to skip no-op writes; Publish button gated on `validateGraph` returning zero issues; status pill + version pointer (`v{N}`) in the header.
- `[✅]` Versions panel — `components/workflow-versions-panel.tsx`. Slide-in side panel toggled from a header button (with count badge), top half lists versions newest-first with `current` badge on the active one, bottom half shows the selected version's frozen graph + trigger as collapsible JSON blocks. Wires `useAutomationVersions`.
- `[✅]` Run inspector — `app/[workspace]/automations/[id]/runs/[runId]/page.tsx`. Status pill per `RunStatus` (running→info, awaiting_*→warning, completed→success, failed→danger), version pointer, Refresh + Cancel toolbar (Cancel gated on terminal status), metadata grid (started / finished / current step / total cost summing step_runs[].cost_cents), step-runs list with per-step status pill + `current` badge matching `run.current_step_id`, collapsible input/output/error JSON, surfaced `idempotency_key` for replay debugging, state-snapshot + trigger-payload JSON. Light 3s refetch loop while non-terminal so the page feels live.
- `[✅]` "Describe in English" panel — Claude prompt `automations.author_from_nl.v1` returns JSON graph; canvas hydrates. *Tool_use schema, Sonnet 4.6 default, review-before-save gate.*
- `[☑️]` Undo/redo on canvas edits.
- `[🏗️]` Schema validator — light validator on the backend (`graph.validate` — `start_node_id` + `nodes` shape + known node types) runs on publish; full client-side validator in `lib/workflow-graph.ts` now covers disconnected nodes (reachability from start), missing required outgoing edges per node type, missing `action.config.action`, missing `branch.config.field`, and dangling edge targets. Type-mismatch checks between adjacent nodes (e.g. branch field vs action output schema) still pending.

**Acceptance criteria**
- `[🏗️]` TC-29 (build 4-step workflow — canvas + palette + drawer + autosave + 18 backend tests shipped; manual UI smoke-test pending toolchain), TC-30 (describe-in-English — backend `generate_from_nl` endpoint + 8 hermetic tests + frontend Describe panel with Apply/Discard review gate; manual UI smoke pending toolchain), TC-31 (draft/publish versioning — backend immutability proven + frontend Publish/Run buttons + status pill + Versions panel listing every snapshot + Run inspector surfacing step outputs against the bound version), TC-32 (validator blocks malformed graphs — Publish button is blocked when `validateGraph` returns any issue; stuck runs cancellable from the Inspector).

**Frontend dependency added**
- `@xyflow/react ^12.3.5` (~140kb gz, MIT). User-approved via AskUserQuestion ahead of `pnpm install`.

---

### `[🏗️]` Phase M9 — Workflow engine completeness + ★★ Agents Marketplace v1 (Epic: Triggers, Actions, Integrations, Marketplace)
*Status:* in progress — trigger dispatcher + 4 of 5 trigger types (record, webhook, schedule, form) + 3 action-expansion phases (HTTP, loop, full CRM-mutate) shipped; AI-condition trigger + Slack OAuth/action + run-inspector retry counts + **Agents Marketplace v1 (M9.S4 — demo-critical, FR-26)** pending · *Estimate:* 7 → 10 days (M9.S4 adds ~3 days) · *Depends on:* M8 · *Covers:* FR-11 (full), FR-21, FR-22, **FR-26** · *Tests:* TC-39, TC-62–TC-65, TC-83, **TC-92–TC-94**

**User stories**
- `[🏗️]` M9.S1 — As an admin, I can use any of the v1 trigger types (record, time, webhook, form, AI condition). *4 of 5 v1 trigger types ship. Phase 1: `apps/automations/triggers.py` dispatcher (`TriggerEvent` dataclass, `fire(event)` matches by `type` against every ACTIVE+published automation in the workspace, `run_automation_with_payload(...)` for explicitly-routed types). **Record**: Contact / Company / Deal create + Deal `stage_changed` post-save handlers dispatch via `transaction.on_commit` so rollbacks don't fire automations. **Webhook** (phase 2a): `WebhookEndpoint` model + public `POST /api/webhooks/{token}/` view with `X-Offside-Signature` HMAC-SHA256 verification (`sha256=<hex>` or bare hex), unknown-token→404, inactive→403, paused→409, success→200+`{run_id}` + atomic `F("fire_count")+1`. **Schedule** (phase 2b): `ScheduleTrigger` model + `automations.scan_schedule_triggers` Beat task running every 60s — parses the 5-field cron via `celery.schedules.crontab` and calls `is_due(last_fired_at or now-61s)`; no-backlog semantics (paused/unpublished automations still stamp `last_fired_at`); bad cron strings logged + skipped without poisoning the sweep. **Form** (phase 2c): `FormEndpoint` model (token + title/description + `is_active` + `rate_limit_per_minute` (default 10) + audit) + public `POST /api/forms/{token}/submit/` view — no HMAC, rate-limited via min-gap = `60 / rate_limit_per_minute` between `last_submission_at` and now; rate-limit hit returns 429 with `Retry-After` header; JSON or form-encoded body lands in `trigger_payload`; paused automation → 409 with audit NOT bumped (forms are user-driven, no need to swallow the submission unlike schedule's no-backlog policy). 34 new tests total (10 dispatcher + 8 webhook + 8 schedule + 8 form). **Pending:** AI condition (periodic LLM eval — likely defers into M11), Gmail Pub/Sub stub (real in M10).*
- `[🏗️]` M9.S2 — As an admin, I can use any v1 action type (CRM mutate, Slack, HTTP, branch, loop, delay, approval). *Phase 1 — `crm.http.request` (outbound HTTP/HTTPS with method allowlist, auth presets none/bearer/basic/custom-header, timeout 1..120s, `expect_json` toggle, follows redirects, response body truncated at 256KB, basic SSRF guard rejecting non-http(s) schemes — DNS-resolution check defers to M11). Phase 2 — `crm.loop` (iterates `items`, runs `inner_action` per item with `{{ item.<path> }}` / `{{ index }}` templating, `on_error: continue | abort`, max_items + 5000 hard cap, self-nest guard; loop-level idempotency caveat documented — per-iteration keys land with M11 sub-graph loop). Phase 3 — CRM-mutate expansion across the M5 entities: `crm.update_contact`, `crm.create_company` + `crm.update_company`, `crm.create_deal` (validates `stage_id` against the pipeline's stages), `crm.update_deal`, `crm.create_task` (validates `related_type` allowlist), `crm.create_note`. Patch-style updates whitelist allowed fields via per-entity `_*_PATCHABLE_FIELDS` sets and route through `_apply_patch` which only saves actually-changed fields (minimal `update_fields=...`). Tampering with `workspace_id` / `created_at` / `created_by` etc. raises `ActionError`. Cross-workspace fetch returns "not found" — same path as the workspace-isolation guard. 46 new tests total (15 HTTP + 14 loop + 17 CRM-mutate). **Pending:** Slack action (depends on M9.S3 OAuth), retry/timeout knobs on inner-action errors.*
- `[☑️]` M9.S3 — As an admin, I can post to Slack channels/DMs from any workflow.
- `[☑️]` **M9.S4 — As an admin, I can install a pre-built workflow agent from the Agents Marketplace with one click.** *Demo-critical (FR-26). Workspace-agnostic curated catalog + one-click install + 4–6 seeded agents. Implementation breakdown below.*

**Engineering tasks**
- `[🏗️]` Trigger registry — webhook (HMAC), record, schedule (Beat-driven), and form-submission endpoint all shipped (see M9.S1 note above). AI-condition + Gmail Pub/Sub stub still pending.
- `[🏗️]` Action registry expansion — `crm.http.request` (HTTP w/ auth presets), `crm.loop` (templated per-item), and CRM-mutate expansion across the M5 entities (`crm.update_contact`, `crm.create_company`, `crm.update_company`, `crm.create_deal`, `crm.update_deal`, `crm.create_task`, `crm.create_note`) all shipped. (Branch + delay already in M7; `crm.create_contact` + `crm.move_deal_stage` from M7.) **13 registered actions total**, all auto-picked-up by `automations.author_from_nl.v1`. Pending: Slack action via OAuth integration (depends on M9.S3).
- `[☑️]` Slack OAuth + connection model in `apps/integrations`.
- `[☑️]` Run inspector enriched — node graph viewer, retry counts, idempotency keys visible.
- `[☑️]` **Agents Marketplace v1** (M9.S4, FR-26) — `apps/marketplace` Django app with:
    1. `MarketplaceAgent` model (slug + name + description + category + icon_emoji + graph JSONField + trigger JSONField + install_count + author + published_at). Workspace-agnostic (no workspace FK).
    2. `WorkspaceAgentInstall` model (workspace + marketplace_agent FK + automation FK + installed_by + installed_at).
    3. Migration `0001_initial.py` hand-authored, depends on `automations.0005_formendpoint`.
    4. DRF: `MarketplaceAgentViewSet` read-only (list + detail) on `GET /api/marketplace/agents/` and `/agents/{slug}/`, **AllowAny** + no auth (catalog is shareable). `POST /api/marketplace/agents/{slug}/install/` workspace-scoped + manager-gated — snapshots agent.graph into a new `Automation` + `AutomationVersion`, sets `published_version`, increments `install_count` atomically, writes `WorkspaceAgentInstall` audit row, returns the new `automation_id`.
    5. Seed script `tools/seeds/marketplace.py` with 4–6 hand-curated agents using only currently-shipped action types: *Lead qualification* (record trigger + branch + crm.create_task), *Deal hygiene sweep* (schedule + crm.loop over stale deals), *Inbound webhook → contact* (webhook + crm.create_contact + crm.create_note), *Stalled-deal nudge* (schedule + crm.http.request → Slack incoming-webhook).
    6. Frontend `/[workspace]/marketplace/` grid page (category filter, install_count badge, icon) + `/[workspace]/marketplace/{slug}/` detail page with read-only canvas preview + Install button. Sidebar entry. Install redirects to `/[workspace]/automations/{id}/` so the user lands in the editor with the freshly published agent loaded.
    7. `lib/api.ts` hooks: `useMarketplaceAgents`, `useMarketplaceAgent`, `useInstallMarketplaceAgent`.
    8. Tests TC-92..TC-94: catalog readable anon, install round-trip (manager-only, creates Automation + AutomationVersion + WorkspaceAgentInstall + bumps install_count), edit-after-install (canvas changes don't propagate back to the catalog).

**Acceptance criteria**
- `[🏗️]` TC-39 (transient retry — M7 idempotency proven; retry-loop visibility pending), TC-62 (Slack connect — pending), TC-63 (post Slack from workflow — pending), TC-64 (inbound webhook fires workflow — **closed**: webhook endpoint + HMAC verification + tests prove fire-on-valid-sig, no-fire-on-bad-sig, audit counter bump), TC-65 (outbound HTTP with bearer — **closed**: `crm.http.request` ships with bearer/basic/custom-header presets, 256KB body cap, `httpx.ConnectError` → ActionError mapping, 15 hermetic tests), TC-83 (advancer step latency budget — pending), **TC-92–TC-94 (Agents Marketplace — pending)**.
- `[🏗️]` 10-step workflow with branch + loop + HITL approve-from-iOS-push works end-to-end. *(Loop action shipped; Slack-on-iOS-push integration pending.)*
- `[☑️]` **Agents Marketplace demo path:** open `/marketplace`, install an agent in one click, land in `/automations/{id}/` with v1 already published, run it manually, see step outputs in the inspector. (FR-26 acceptance.)

---

### `[☑️]` Phase M10 — Gmail + Calendar sync (Epic: Comms Source-of-Truth)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M9 · *Covers:* FR-9, FR-10 · *Tests:* TC-25–TC-28, TC-41

**User stories**
- `[☑️]` M10.S1 — As a rep, I connect my Gmail and see threads with each contact within a minute.
- `[☑️]` M10.S2 — As a rep, replies arrive in the contact's activity feed in real time.
- `[☑️]` M10.S3 — As a rep, I send email from the contact view as my Gmail account.
- `[☑️]` M10.S4 — As a rep, I see GCal meetings on each deal.

**Engineering tasks**
- `[☑️]` Gmail OAuth (read + send + push scopes); thread + message ingestion service.
- `[☑️]` Pub/Sub topic + subscription + verified domain; `/gmail/push` endpoint.
- `[☑️]` Send-mail action wired to Gmail API.
- `[☑️]` Threading: matching algorithm to associate threads with contact emails.
- `[☑️]` GCal OAuth + event sync (read + write).
- `[☑️]` "Email received" workflow trigger; `email_sent` activity rows from outbound.

**Acceptance criteria**
- `[☑️]` TC-25 (connect Gmail), TC-26 (send from contact view), TC-27 (inbound creates activity row), TC-28 (GCal meetings on deal), TC-41 (thread summary appears).

---

### `[☑️]` Phase M11 — AI surfaces in CRM (Epic: AI Everywhere v1)
*Status:* pending · *Estimate:* 6 days · *Depends on:* M10 · *Covers:* FR-13, FR-15, FR-16, FR-20 (Claude column-mapping upgrade), NFR-6 · *Tests:* TC-40–TC-42, TC-46–TC-50, TC-86, TC-91

**User stories**
- `[☑️]` M11.S1 — As a rep, AI drafts and reply-suggestions appear inline in every contact + deal view.
- `[☑️]` M11.S2 — As a rep, new contacts and companies auto-enrich (industry, size, score) within 60 seconds.
- `[☑️]` M11.S3 — As a rep, quiet deals show calm "next-action" suggestions I can dismiss or convert to a workflow.

**Engineering tasks**
- `[☑️]` `packages/ai` — real model router (Claude default; OpenAI/Gemini fallback), prompt registry, structured-output retry-with-correction, telemetry emitter.
- `[☑️]` `backend/apps/ai` — Python twin with the same prompt names + Pydantic schemas.
- `[☑️]` Prompts: `comms.draft_reply.v1`, `comms.summarize_thread.v1`, `comms.summarize_meeting.v1`, `enrichment.company.v1`, `scoring.lead.v1`, `suggestions.next_action.v1`, `imports.suggest_column_mapping.v1` (replaces M4 heuristic).
- `[☑️]` Streaming surface in web — server-sent events through Next.js route handler.
- `[☑️]` Per-workspace daily token budget; over-budget queue + admin notice.
- `[☑️]` Provider fallback wiring; "fallback model" badge in admin telemetry.

**Acceptance criteria**
- `[☑️]` TC-40 (drafts stream ≤1.5s P95), TC-41 (thread summary), TC-42 (meeting summary), TC-46 (enrichment fills fields), TC-47 (token budget halts enrichment), TC-48 (manual re-score), TC-49 (quiet-deal suggestion), TC-50 (suggestion → workflow), TC-86 (provider fallback), TC-91 (no cross-workspace leak).

---

### `[☑️]` Phase M12 — NL data layer + pgvector + global search (Epic: Conversational Data Access)
*Status:* pending · *Estimate:* 5 days · *Depends on:* M11 · *Covers:* FR-14, FR-19 · *Tests:* TC-43–TC-45, TC-55–TC-57

**User stories**
- `[☑️]` M12.S1 — As a manager, I type natural-language queries in cmd-K and see a filtered list within 2 seconds.
- `[☑️]` M12.S2 — As a rep, fuzzy queries like "deals that smelled risky" still find the right results via vector rerank.
- `[☑️]` M12.S3 — As a rep, my saved NL views persist and are shareable with my workspace.

**Engineering tasks**
- `[☑️]` Embedding worker — Celery task on entity create/update writes to `embedding` table with HNSW index.
- `[☑️]` Prompt `data.nl_to_filter_dsl.v1` — schema-aware (includes custom fields), schema cached per workspace per schema version.
- `[☑️]` Filter DSL evaluator promoted to a first-class server-side endpoint `/api/query/`.
- `[☑️]` Hybrid search: FTS first; vector rerank when FTS confidence is low.
- `[☑️]` Saved views in cmd-K (sharing semantics: workspace-visible by default; private if marked).

**Acceptance criteria**
- `[☑️]` TC-43 (NL query in cmd-K), TC-44 (fuzzy query via vector), TC-45 (saved NL view), TC-55 (cmd-K open ≤80ms ranking correct), TC-56 (recent searches), TC-57 (search across notes + emails).

---

### `[☑️]` Phase M13 — Agentic mode + HITL (Epic: Agent Autonomy v1)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M12 · *Covers:* FR-17, completes FR-23 (push + edit), FR-24 (push), FR-6 (iOS tasks tab) · *Tests:* TC-37, TC-38, TC-51–TC-54, TC-70

**User stories**
- `[☑️]` M13.S1 — As an admin, I can set per-action-type policies (`suggest` / `approve` / `autonomous`) for the workspace.
- `[☑️]` M13.S2 — As a rep, I can toggle "Agent assist" on a specific deal and see the agent propose actions.
- `[☑️]` M13.S3 — As a manager, I receive iOS pushes for HITL approvals and can act without unlocking the device.
- `[☑️]` M13.S4 — As any user, autonomous reversible actions show a 60-second undo affordance.

**Engineering tasks**
- `[☑️]` Agent policy table UI + persistence (model already exists in `apps/automations` from M7).
- `[☑️]` Agent loop — Claude Opus planner returns proposed actions; per-action policy gates dispatch; HITL fans out to in-app + email + iOS push.
- `[☑️]` iOS push notification actions — Approve / Reject / Snooze (deferred 1h) on lock-screen + APNs registration round-trip (deferred from M6).
- `[☑️]` Undo system — for reversible action types, expose a 60s undo toast; record undo in activity.
- `[☑️]` Audit row enrichment — every agent action logs prompt + model + cost + decider + decision.
- `[☑️]` iOS edit + tasks tab + custom-fields panel + activity feed (deferred from M6).

**Acceptance criteria**
- `[☑️]` TC-37 (iOS push approve), TC-38 (60s undo on autonomous), TC-51 (workspace policy table), TC-52 (per-deal Agent assist), TC-53 (mixed autonomous + approve batch), TC-54 (audit log captures everything), TC-70 (lock-screen approve).

---

### `[☑️]` Phase M14 — Reports + saved views + dashboards (Epic: Visibility)
*Status:* pending · *Estimate:* 4 days · *Depends on:* M13 · *Covers:* FR-18, FR-25 · *Tests:* TC-72–TC-74, TC-89

**User stories**
- `[☑️]` M14.S1 — As a manager, on workspace home I see this week's pipeline + the team's activity.
- `[☑️]` M14.S2 — As a viewer, I can drill from a counter into the underlying records.
- `[☑️]` M14.S3 — As an admin, I can filter the activity log and export a 30-day audit slice as CSV (FR-25).

**Engineering tasks**
- `[☑️]` Workspace home dashboard — counters (deals by stage, won this month, overdue tasks), funnel chart, activity-over-time chart.
- `[☑️]` Cached aggregates — periodic Beat task refreshes (every 5 min) writes to a `dashboard_cache` table.
- `[☑️]` Charting library — Tremor or Visx (decision deferred to phase start; both work with brand tokens).
- `[☑️]` Saved views surfaced on workspace home.
- `[☑️]` Audit log admin UI — filterable list + CSV export (FR-25).
- `[☑️]` Bulk-action UI on contact/company list (deferred from M4 — TC-14).

**Acceptance criteria**
- `[☑️]` TC-72 (workspace home loads ≤500ms P95), TC-73 (drill from counter), TC-74 (charts respect color-not-sole-signal), TC-89 (30-day audit slice + CSV export), TC-14 (bulk edit).

---

### `[☑️]` Phase M15 — Polish (Epic: Production Readiness)
*Status:* pending · *Estimate:* 7 days · *Depends on:* M14 · *Covers:* NFR-1, NFR-2, NFR-4 · *Tests:* TC-78–TC-87 across the suite

**User stories**
- `[☑️]` M15.S1 — As any user, every flow has thoughtful empty / loading / error states.
- `[☑️]` M15.S2 — As any user, the marketing-grade `/login` + `/signup` + landing route feels like a polished product.
- `[☑️]` M15.S3 — As an SRE, every page meets perf budgets; Lighthouse ≥ 95.

**Engineering tasks**
- `[☑️]` Empty-state inventory across every route; design + copy pass.
- `[☑️]` Loading skeletons on every async surface (no blank flash).
- `[☑️]` Error boundary + toast system; provider fallback messaging.
- `[☑️]` Lighthouse / axe runs in CI; fail-the-build threshold set.
- `[☑️]` iOS regression sweep; offline edits with conflict-resolution polish.
- `[☑️]` Marketing-grade `/login` + `/signup` reusing offside.ai marketing-site shell.
- `[☑️]` Manual screen-reader pass (TC-79 deferred from M3) + axe CI gate (TC-78 deferred from M3).
- `[☑️]` `wake_up_sweep` PeriodicTask data migration for `DatabaseScheduler` (deferred from M7).

**Acceptance criteria**
- `[☑️]` TC-78–TC-88 pass.
- `[☑️]` Lighthouse ≥ 95 perf/a11y on web.
- `[☑️]` iOS App Store review checklist green.

---

## Post-MVP placeholders

Each phase below is a **placeholder**. Real prioritization happens after MVP launch + first-cohort interviews. Order is not committed — it's a working hypothesis. Engineering effort is "T-shirt" sized only.

### `[☑️]` Phase POST-1 — Stripe / billing
*Covers PRD:* POST-1 · *Size:* L · *Depends on:* M15
- `[☑️]` Plan tiers (Free trial → Starter → Team → Scale).
- `[☑️]` Per-seat pricing + AI-token soft caps; metering of token usage to Stripe.
- `[☑️]` Customer portal for self-serve plan changes.
- `[☑️]` Dunning + grace period; workspace lockout on chronic non-payment.
- `[☑️]` Webhook handler for invoice.paid / subscription.updated.
- `[☑️]` Open question: usage-based vs hybrid pricing — needs price-test infra (POST-15 marketplace might cover).

### `[☑️]` Phase POST-2 — Long-tail integrations
*Covers PRD:* POST-2 · *Size:* XL (multi-quarter) · *Depends on:* M15
- `[☑️]` HubSpot bidirectional sync (read + write back) — extends FR-20 import beyond CSV.
- `[☑️]` Pipedrive bidirectional sync — extends FR-20.
- `[☑️]` Salesforce read-only mirror + selective write.
- `[☑️]` Microsoft 365 — Outlook + Calendar parity to Gmail/GCal.
- `[☑️]` Linear, Notion, Zoom, Twilio (SMS/calls), DocuSign.
- `[☑️]` Pattern: each integration = OAuth + ingestion service + webhook handler + workflow trigger/action set + a connector card in Settings.

### `[☑️]` Phase POST-3 — Multi-language i18n (web + iOS)
*Covers PRD:* POST-3 · *Size:* L · *Depends on:* M15
- `[☑️]` ICU message format; translation pipeline (Crowdin / Lokalise).
- `[☑️]` RTL support evaluation — likely punted to a later phase.
- `[☑️]` Date/number locale handling.
- `[☑️]` AI prompts respect user locale (German rep gets German drafts).

### `[☑️]` Phase POST-4 — Native Android app
*Covers PRD:* POST-4 · *Size:* XL · *Depends on:* M15, partial POST-3
- `[☑️]` Decision: Kotlin Multiplatform (share with iOS where possible) vs native Compose.
- `[☑️]` APNs equivalent: FCM.
- `[☑️]` Re-test full E2E suite per TESTING.md on Android targets.

### `[☑️]` Phase POST-5 — Enterprise: SSO/SCIM/audit/sandbox
*Covers PRD:* POST-5 · *Size:* L · *Depends on:* M15
- `[☑️]` SAML/OIDC SSO (WorkOS or built-in).
- `[☑️]` SCIM provisioning.
- `[☑️]` 7-year audit retention with object-storage cold tier.
- `[☑️]` Custom role builder (granular permission matrix).
- `[☑️]` Per-workspace sandbox environment (separate Postgres schema + Redis namespace).

### `[☑️]` Phase POST-6 — Suite app: Crunch (AI-native spreadsheet)
*Covers PRD:* POST-6 · *Size:* XL · *Depends on:* M15
- `[☑️]` Real `frontend-web` sibling app at `crunch-web/` (replace M0 placeholder). Shared `packages/ui`, `packages/ai`, `packages/auth-utils`.
- `[☑️]` Distinct backend or new Django app inside `backend/` (decision deferred — likely separate service to keep CRM stable).
- `[☑️]` Spreadsheet engine — formula evaluator, AI-cell with prompt registry.

### `[☑️]` Phase POST-7 — Suite app: Design (AI-native app design tool)
*Covers PRD:* POST-7 · *Size:* XL · *Depends on:* POST-6 (Crunch shakes out shared-package gaps first)
- `[☑️]` Canvas + design system primitives (`@offside/ui` extended with editor surfaces).
- `[☑️]` AI primitives: layout generator, copy generator, theme generator.

### `[☑️]` Phase POST-8 — Suite app: Director (AI-native marketing suite)
*Covers PRD:* POST-8 · *Size:* XL · *Depends on:* POST-6, POST-7
- `[☑️]` Campaign builder, audience segments (re-use CRM contact schema), AI ad-copy + creative.
- `[☑️]` Cross-product data model: CRM contact = Director audience member.

### `[☑️]` Phase POST-9 — Advanced agent capabilities
*Covers PRD:* POST-9 · *Size:* L · *Depends on:* M15
- `[☑️]` Multi-step planning across many records ("warm up 50 leads this week with personalized outreach").
- `[☑️]` Agent-to-agent handoff for complex cross-functional flows.
- `[☑️]` Voice-call agents (Twilio + AI).
- `[☑️]` Autonomous prospecting from public data.

### `[☑️]` Phase POST-10 — Workflow advanced features
*Covers PRD:* POST-10 · *Size:* L · *Depends on:* M15
- `[☑️]` Sub-workflows (call workflow A from workflow B with typed I/O).
- `[☑️]` Parallel fan-out + join steps.
- `[☑️]` Conditional rollout (run new version on 10% of records before full deploy).
- `[☑️]` Workflow templates marketplace (community-contributed).
- `[☑️]` Durable workflow versioning beyond MVP semantics.

### `[☑️]` Phase POST-11 — Reporting v2
*Covers PRD:* POST-11 · *Size:* L · *Depends on:* M15
- `[☑️]` Custom dashboard builder (drag-drop chart blocks).
- `[☑️]` Scheduled report email (PDF + CSV).
- `[☑️]` Formula fields and lookup fields on entities.
- `[☑️]` BI-quality drill-down + pivoting.
- `[☑️]` CSV/Excel export from any list view.

### `[☑️]` Phase POST-12 — Mobile features (iPad, Watch, Catalyst, offline-first edits)
*Covers PRD:* POST-12 · *Size:* L · *Depends on:* M15
- `[☑️]` iPad-optimized layouts with multi-column.
- `[☑️]` Apple Watch complications for "today" + push-approve.
- `[☑️]` Mac Catalyst.
- `[☑️]` Offline-first edits with conflict resolution (merge strategy per field).
- `[☑️]` Full-text search on-device.

### `[☑️]` Phase POST-13 — Compliance & data residency
*Covers PRD:* POST-13 · *Size:* XL · *Depends on:* POST-5
- `[☑️]` SOC 2 Type 2 audit prep.
- `[☑️]` ISO 27001.
- `[☑️]` GDPR DPA + EU data residency.
- `[☑️]` HIPAA where vertical-relevant (healthcare sales orgs).
- `[☑️]` Region-specific deployments (Postgres replicas in EU/APAC).

### `[☑️]` Phase POST-14 — Public API + developer portal
*Covers PRD:* POST-14 · *Size:* M · *Depends on:* M15
- `[☑️]` API tokens per workspace with scopes.
- `[☑️]` Public OpenAPI spec at `developers.offside.ai`.
- `[☑️]` Sample SDKs (TypeScript, Python).
- `[☑️]` Developer docs site.
- `[☑️]` Rate limiting + usage analytics per token.

### `[☑️]` Phase POST-15 — Marketplace + extensions
*Covers PRD:* POST-15 · *Size:* L · *Depends on:* POST-14
- `[☑️]` Custom workflow nodes contributed by partners (sandboxed execution).
- `[☑️]` Workspace-installable AI prompts.
- `[☑️]` Branded automation templates.
- `[☑️]` Revenue share for paid extensions (depends on POST-1 billing).

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

*Legend:* `[✅]` shipped · `[🏗️]` in progress · `[☑️]` pending. Full key at top of file.

| Phase | Days | Status |
|---|---|---|
| M0  | 3 | `[✅]` |
| M1  | 3 | `[✅]` |
| M2  | 4 | `[✅]` |
| M3  | 3 | `[✅]` |
| M4  | 4 | `[✅]` |
| M5  | 4 | `[✅]` |
| M6  | 5 | `[✅]` |
| M7  | 7 | `[✅]` |
| M8  | 7 | `[🏗️]` |
| M9  | 10 | `[🏗️]` |
| M10 | 7 | `[☑️]` |
| M11 | 6 | `[☑️]` |
| M12 | 5 | `[☑️]` |
| M13 | 7 | `[☑️]` |
| M14 | 4 | `[☑️]` |
| M15 | 7 | `[☑️]` |
| **Total** | **86 days** | **8 of 16 milestones complete** |

Calendar projection (single senior eng, normal coordination overhead): **~16–19 weeks** of focused build → **5.5–7.5 months**. Earliest demo-credible internal release: end of M5 (~5 weeks). Earliest "feels like Offside" milestone: end of M11 (~12 weeks).

---

## Status updates

This file gets a one-line status tick at the top of each phase as the project advances. Substantive scope changes get a `## Revision N — date` block at the bottom describing the diff.

### Revision 2 — 2026-05

Added per-task `[✅]/[🏗️]/[☑️]` checkboxes throughout. M0–M7 marked complete (matching MEMORY.md commits `5375384` … `e69dfa3`). Deferred items inside completed milestones flagged ☑️ with the milestone they roll forward to (M6 cache + APNs + tasks tab → M13; M3 axe-clean + screen-reader pass → M15; M7 HITL HTTP endpoint → M7 phase 2; M7 PeriodicTask migration → M15). M14 picked up FR-25 audit-log admin UI + TC-14 bulk edit to match PRD.

### Revision 3 — 2026-05 — M8 backend slice

M8 flipped from ☑️ to 🏗️ as the backend portion landed:

- **Model layer.** New `AutomationVersion` (immutable snapshot, unique on `(automation, version_number)`), `Automation.published_version` FK (SET_NULL), `AutomationRun.version` FK (PROTECT, nullable for M7 backward compat). Migration `0002_automationversion.py`.
- **Runtime.** `tasks.publish_automation` snapshots draft → new version, bumps `Automation.version`, flips DRAFT→ACTIVE on first publish, validates graph. `tasks.cancel_run` is idempotent on terminal status. `kick_off` auto-attaches `automation.published_version`. `run_advancer` and `resume_after_hitl` read the frozen `version.graph` (M7 versionless runs fall back to the draft graph for backward compat).
- **DRF.** `AutomationViewSet` (CRUD + `publish`, `versions`, `start_run` actions), `AutomationRunViewSet` (read-only list/detail with `step_runs` inlined for the inspector + `cancel` action), `AutomationVersionViewSet` (flat read-only). Manager-gated on writes/publish/start/cancel. Wired into `offside_crm/urls.py`.
- **Tests.** 18 new: load-bearing `test_in_flight_run_unaffected_by_draft_edit` proves a draft edit can't change a running v1 run's output. Covers TC-29 (publish creates v1), TC-30 (edit + republish → v2 alongside v1), TC-32 (cancel a stuck delay run); plus workspace isolation, invalid-graph rejection, kick_off fallback paths, cancel idempotency.

Remaining for M8: React Flow canvas, node config drawer, describe-in-English panel, undo/redo, full structural validator, HITL HTTP decide endpoint.

### Revision 4 — 2026-05 — M8 canvas slice

M8 frontend canvas landed; M8.S1 flipped from ☑️ to ✅, M8.S2 remains 🏗️ pending the run inspector.

- **Lib.** New `frontend-web/lib/workflow-graph.ts` — `graphToFlow` / `flowToGraph` bidirectional conversion (positions + label carried as editor-only keys the backend round-trips), `generateNodeId`, `nodePreset` defaults per node type, `validateGraph` (reachability from start, missing outgoing edges per node type, missing per-type config, dangling edge targets).
- **Components.** New `components/workflow-canvas.tsx` (React Flow + ReactFlowProvider, custom `AutomationNodeView` with `true`/`false`, `approve`/`reject`, `next` source handles, dotted Bone background, hidden attribution, MiniMap + Controls, HTML5 drag-from-palette + screenToFlowPosition drop, debounced 300ms autosave with hash gate, inline ValidationOverlay). New `components/workflow-node-palette.tsx` (draggable buttons per node type with brand-tokened cards). New `components/workflow-node-drawer.tsx` (per-node-type forms — action name + JSON input, delay seconds, approval summary + TTL, branch field/op/value, wait_for_event key — with a live JSON textarea that surfaces parse errors inline, Set-as-start, Delete, label editor).
- **Pages.** New `app/[workspace]/automations/page.tsx` (list page with empty state + brand cards showing version/node-count/last-update + "+ New workflow" creates a draft and routes to the editor). New `app/[workspace]/automations/[id]/page.tsx` (editor shell: workflow-name input with onBlur PATCH, save indicator with bone-rooted color states, Run button calling `start_run` and disabled when no published version, Publish button gated on `validateGraph` issues, status pill, recent-runs footer linking to inspector).
- **API client.** `lib/api.ts` grew Automation / AutomationVersion / AutomationRun / AutomationStepRun / AutomationGraph / AutomationNode TS types + hooks (`useAutomations`, `useAutomation`, `useCreateAutomation`, `useUpdateAutomation`, `usePublishAutomation`, `useAutomationVersions`, `useStartAutomationRun`, `useAutomationRuns`, `useAutomationRun`, `useCancelAutomationRun`).
- **Wiring.** Sidebar Automations entry flipped from `comingSoon` to live. Command palette gained an Automations item under Navigate. `globals.css` imports `@xyflow/react/dist/style.css`. `package.json` adds `@xyflow/react ^12.3.5`.
- **Brand-token fixes.** Caught during the pass: `StatusPillTone "positive"` → `"success"`; nonexistent `clay`/`positive` Tailwind colors replaced with the StatusPill danger/success hexes (`#8E3B30`, `#3B6A4A`) and the `#c98f89` clay hex for the approval node border.

Remaining for M8: run inspector UI (task #4), describe-in-English panel + Claude prompt + telemetry (task #3), HITL HTTP decide endpoint, undo/redo. Manual UI smoke pending `pnpm install && pnpm dev` once the toolchain is up — no `pnpm`/`node` were available on this machine to typecheck the frontend slice.

### Revision 5 — 2026-05 — M8 versions panel + run inspector

M8.S2 flipped from 🏗️ to ✅ as the two remaining frontend pieces landed.

- **Versions panel.** New `frontend-web/components/workflow-versions-panel.tsx`. Slide-in panel on the editor's right edge (`absolute inset-y-0 right-0`, shadow-soft-3). Top half scrolls through `AutomationVersion` rows newest-first with version number, published_at, published_by, and a tan-bordered `current` badge on the row matching `automation.published_version`. Selecting a row reveals the bottom half: `Eyebrow` header, node-count summary, and two collapsible `<details>` JSON blocks (`graph`, `trigger`). Wires the already-shipped `useAutomationVersions` hook — no new API surface needed.
- **Editor toolbar.** `app/[workspace]/automations/[id]/page.tsx` gains a `Versions` button in the header (with a tiny font-mono count badge) that toggles the panel. Canvas + panel are wrapped in a shared `relative flex-1` container so the panel's absolute positioning anchors to the canvas area instead of the page.
- **Run inspector page.** New `app/[workspace]/automations/[id]/runs/[runId]/page.tsx`. Back-link to the parent workflow, `StatusPill` colored per `RunStatus` (running→info, awaiting_*→warning, completed→success, failed→danger), version-pointer badge, Run #N title with tan-period.
- **Inspector toolbar.** Refresh button (manual `run.refetch()`) + Cancel button gated on `TERMINAL.has(status)` (set: completed, failed, cancelled). Cancel hits `useCancelAutomationRun`, surfaces failures inline. Inflight runs (`!TERMINAL.has`) get a 3s polling loop while the page is open so the inspector feels live.
- **Metadata grid.** Started / Finished / Current step / Total cost (sums `step_runs[].cost_cents`). Cost formatted via Intl.NumberFormat USD with 4-decimal precision under 100¢ for the cheap-LLM-call case.
- **Step runs list.** Per-step card with `step_id`, attempt counter, status pill, and a tan ring + `current` badge when `step_id === run.current_step_id`. Header row exposes started/finished timestamps, model, cost. Body surfaces the load-bearing `idempotency_key` line for replay debugging plus three collapsible JSON blocks: input, output, and error (when present).
- **Bottom sections.** `state_snapshot` (per-node outputs available to downstream `{{ <node_id>.<field> }}` templates) and `trigger_payload` as collapsible JSON blocks. Tan-text Eyebrow labels throughout.
- **Wiring fix.** Closes the per-run links in the editor footer that previously 404'd.

Remaining for M8: M8.S3 (NL→graph prompt + canvas hydration + cost/latency telemetry), HITL HTTP decide endpoint, undo/redo, type-mismatch validator. Manual UI smoke still pending toolchain.

### Revision 6 — 2026-05 — M8.S3 describe-in-English

M8.S3 flipped from ☑️ to ✅. New `apps/ai` Django app + `generate_from_nl` endpoint + frontend Describe panel.

- **New backend app `apps/ai`** — registered in `INSTALLED_APPS` (slot was reserved). Five files: `models.py` (the `AICall` telemetry row with workspace, prompt_name, model, status, tokens_in/out, cost_cents, latency_ms, optional `run` FK + `step_id` for run-time calls, error, metadata; two indexes for daily-budget aggregation), `prompts.py` (registry built on a `Prompt(name, model, build)` dataclass; `automations.author_from_nl.v1` ships the system prompt with the registered action names interpolated from `apps.automations.actions.all_names()`, the user message template, and a Claude `tool_use` schema forcing a `build_graph` JSONSchema return so the model can't drift from graph shape), `client.py` (thin wrapper that calls `anthropic.Anthropic().messages.create(...)`, parses the tool_use block, writes an `AICall` row on every call success-or-failure, hardcodes per-Mtok pricing for `claude-sonnet-4-6`, `claude-opus-4-7`, `claude-haiku-4-5-20251001` so cost telemetry isn't zero; `set_override_caller(fn)` test hook short-circuits the real SDK), `services.py` (public `generate_automation_graph(workspace, description, requested_by, workspace_context)` routes through `apps.automations.graph.validate` — invalid graphs raise `AIResponseError` and the client wrapper still logs the call), `admin.py` (read-only `AICallAdmin` browser for the telemetry table). `exceptions.py` defines `AIClientError` (transport) + `AIResponseError` (shape). `migrations/0001_initial.py` is hand-authored and depends on `automations.0002_automationversion` (so `AICall.run` can FK to AutomationRun).
- **DRF.** `AutomationViewSet.generate_from_nl` action — `POST /api/automations/{id}/generate_from_nl/` with `{description, workspace_context?}` returns `{graph, model, tokens_in, tokens_out, latency_ms}` WITHOUT saving (frontend reviews + PATCHes via the existing autosave path). Manager-gated. Maps `AIResponseError → 400`, `AIClientError → 502`.
- **8 hermetic tests** in `apps/ai/tests/test_generate.py`. Service: happy path + AICall row written; empty tool input → `AIResponseError`; bad graph shape → `AIResponseError` (via `graph.validate`); transport failure → `AIClientError` + AICall row with status=error and trimmed stack; prompt registry resolution + build kwargs shape. DRF: 200 success, 400 missing description, 502 provider failure. Every test runs against `set_override_caller`, never the real API.
- **Frontend `lib/api.ts`.** `GenerateFromNLResponse` type + `useGenerateFromNL(workspaceId)` mutation hook (no cache invalidation — the response is a preview, not state).
- **Frontend `components/workflow-nl-panel.tsx`.** Collapsible two-column panel between the editor header and the canvas. Left: `<Eyebrow>` + close button + textarea + Generate button + three example-prompt chips that prefill the textarea. Right: `<Eyebrow>` + node count + token + latency telemetry + JSON preview + **Apply to canvas** / **Discard** buttons. Apply routes through the existing graph-change handler so it hits the same autosave path — nothing publishes until the user explicitly hits Publish.
- **Editor toolbar.** Gained a **Describe** button with a small tan `AI` eyebrow tag, sitting next to Versions / Run / Publish. Three new state slots in `[id]/page.tsx`: `nlOpen`, `nlPreview`, `nlError`. The Discard handler clears preview + error; Close also resets so reopening starts blank.

No new deps added — `anthropic==0.42.0` was already pinned. Test pytest + manual UI smoke pending the Docker toolchain.

M8 close-out remaining: HITL HTTP decide endpoint (`/api/hitl/<token>/decide/` view over the M7 `hitl.py` service), undo/redo on the canvas, type-mismatch validator between adjacent nodes, manual UI smoke once `pnpm install && pnpm dev` runs.

### Revision 7 — 2026-05 — M9.S1 phase 1 + 2a (record + webhook triggers)

M9 opened; M9.S1 partially landed.

- **Trigger dispatcher.** New `backend/apps/automations/triggers.py`. `TriggerEvent` dataclass keyed on `type` ∈ {manual, record, webhook, schedule, form, ai_condition}. `fire(event)` filters every `ACTIVE` automation in the workspace with a non-null `published_version`, runs `_matches(automation.trigger, event)`, and creates an `AutomationRun(version=automation.published_version)` per match — `kick_off(run)` walks it through the M7 runtime. Manual deliberately never auto-fires (default config for new workflows). `run_automation_with_payload(automation, *, trigger_type, payload)` is the explicit-routing helper used by webhook (and soon schedule/form) where the URL/cron is the routing — skips workspace-wide matching.
- **Record trigger.** `apps/activities/signals.py` post-save handlers (Contact / Company / Deal create + Deal `stage_changed`) now call `emit_record(...)` via `transaction.on_commit(...)` so a rollback can't fire automations against state the user never persisted. Trigger config shape: `{type: "record", entity_type: "contact"|"company"|"deal", event: "created"|"updated"|"stage_changed"}`. 10 new tests in `test_triggers.py`: direct fire() matchers (entity/event/workspace/draft/manual short-circuit) + end-to-end with `@pytest.mark.django_db(transaction=True)` (Contact/Company/Deal create kicks off matching automation, Deal stage_id update fires `stage_changed` but not `created`, trigger_payload carries entity_type/record_id/record-specific fields).
- **Webhook trigger.** New `WebhookEndpoint` model on `apps.automations` (workspace + automation FK + URL-safe `token` (unique) + HMAC `secret` + `label` + `is_active` + audit fields `created_by` / `created_at` / `fire_count` / `last_fired_at`). Migration `0003_webhookendpoint.py` hand-authored. Public `POST /api/webhooks/{token}/` via `WebhookFireView(APIView)` with `authentication_classes = []` + `permission_classes = [AllowAny]` — unknown token → 404, inactive endpoint → 403, bad/missing `X-Offside-Signature` → 401 (HMAC-SHA256 constant-time compare; accepts `sha256=<hex>` or bare hex), paused automation / no published version → 409, success → 200 + `{run_id}` + atomic `F("fire_count")+1` and `last_fired_at` stamp. JSON body becomes `trigger_payload` (plus `type: "webhook"` + `webhook_token`); non-JSON falls back to `{"raw": ...}` so opaque payloads still fire. `WebhookEndpointAdmin` registered so workspace admins can mint endpoints from Django admin (frontend CRUD will follow with M9.S2). 8 new tests in `test_webhooks.py`: valid signature fires + completes + trigger_payload merged; bare-hex sig accepted; bad sig 401 + no run; missing sig 401; unknown token 404; inactive endpoint 403; paused automation 409 + no run; non-JSON body → `{raw}` payload + 200.
- **Acceptance.** TC-64 (inbound webhook fires workflow) now closed by the test slice. Manual smoke (running curl against `/api/webhooks/{token}/` with a real signed payload) pending Docker toolchain.

Remaining for M9.S1: **schedule trigger** (Celery Beat + `django-celery-beat` PeriodicTask), **form trigger** (public unsigned POST with rate limit), **AI condition trigger** (periodic LLM eval over recent activity — likely defers into M11), Gmail Pub/Sub stub (real in M10).

Remaining for M9 overall: M9.S2 (CRM mutate / Slack / HTTP / loop action expansion) and M9.S3 (Slack OAuth + post action).

### Revision 8 — 2026-05 — M9.S1 phase 2b (schedule trigger)

Third trigger type lands. M9.S1 remains 🏗️ (form + AI condition still open).

- **Model.** New `ScheduleTrigger` on `apps.automations` — workspace + automation FK + `cron_expression` (5-field cron, e.g. "0 9 * * MON") + `timezone_name` (default UTC) + `label` + `is_active` + audit fields (`last_fired_at`, `fire_count`, `created_by`, `created_at`, `updated_at`). Workspace-scoped manager + two indexes: `(is_active, last_fired_at)` for the sweep query and `(workspace, is_active)` for per-workspace lookups. Migration `0004_scheduletrigger.py` hand-authored, depends on `0003_webhookendpoint`.
- **Beat task.** `automations.scan_schedule_triggers` in `tasks.py`. Runs every 60s per a new `CELERY_BEAT_SCHEDULE` entry (next to the existing `wake_up_sweep`). Walks `is_active=True` rows; for each, parses the 5-field cron string and builds `celery.schedules.crontab(minute, hour, day_of_month, month_of_year, day_of_week)`. Calls `crontab.is_due(anchor)` where `anchor = last_fired_at or (now - 61s)` so first-scan-after-create evaluates immediately. Due rows call `triggers.run_automation_with_payload(automation, trigger_type="schedule", payload={schedule_trigger_id, cron})` and atomically bump `fire_count` + stamp `last_fired_at`. **No-backlog semantics**: `last_fired_at` is bumped even when no run is created (paused automation or no published version), so un-pause doesn't fire a backlog. Bad cron strings are logged + skipped without poisoning the sweep.
- **Admin.** `ScheduleTriggerAdmin` registered so an admin can wire schedules from Django admin today (UI follows in M9.S2).
- **Tests.** 8 new in `apps/automations/tests/test_schedules.py`: due cron fires + completes the run + bumps audit counters; inactive schedule skipped; recently-fired daily cron (last_fired_at 5m ago) skipped; **paused-automation no-backlog** test (sweep consumes the trigger, no run created, audit still bumped); bad cron logged + skipped without blocking other triggers in the same sweep; empty workspace returns 0; multiple schedules on same automation each fire independently; first sweep with `last_fired_at=None` fires immediately. No `freezegun` needed — tests use cron strings due every minute and dial `last_fired_at` into the past.

No new deps — `celery.schedules.crontab` is already pulled in by `celery==5.4.0`.

Remaining for M9.S1: form trigger (public unsigned POST + rate limit), AI condition (likely defers into M11), Gmail Pub/Sub stub (M10).

### Revision 9 — 2026-05 — M9.S1 phase 2c (form trigger)

Fourth trigger type lands. 4 of 5 v1 trigger types now ship (record, webhook, schedule, form). M9.S1 remains 🏗️ — only AI condition + Gmail Pub/Sub stub left.

- **Model.** New `FormEndpoint` on `apps.automations` — workspace + automation FK + URL-safe `token` (unique) + `title` + `description` + `is_active` + `rate_limit_per_minute` (default 10) + audit (`last_submission_at`, `submission_count`, `created_by`, `created_at`). Workspace-scoped manager + `(workspace, is_active)` index. Migration `0005_formendpoint.py` hand-authored, depends on `0004_scheduletrigger`.
- **Public endpoint.** `POST /api/forms/{token}/submit/` via `FormSubmitView(APIView)` with `authentication_classes = []` + `permission_classes = [AllowAny]`. No HMAC (different from webhook — form submissions are about the captured content, not authenticated identity). Rate limit enforced inline: min-gap = `60 / rate_limit_per_minute` seconds between `last_submission_at` and `now`; over-limit returns 429 with `Retry-After` header + `{retry_after_seconds}` body. Unknown token → 404, inactive → 403, paused automation / no published version → 409 (and audit NOT bumped, unlike schedule's no-backlog stance — forms are user-driven so we don't need to swallow the submission). Success → 200 + `{run_id}` + atomic `F("submission_count") + 1` and `last_submission_at` stamp. JSON body becomes `trigger_payload` (plus `type: "form"` + `form_token`); form-encoded multipart falls back to `request.data`; opaque bytes get `{"raw": ...}`.
- **URLs.** New `path("forms/<str:token>/submit/", FormSubmitView.as_view(), name="form-submit")` next to the M9.S1 phase-2a webhook path.
- **Admin.** `FormEndpointAdmin` registered alongside `WebhookEndpointAdmin` + `ScheduleTriggerAdmin`.
- **Tests.** 8 new in `apps/automations/tests/test_forms.py`: JSON submission fires + audit bumped + `form_token` in payload; form-encoded (multipart) also fires + carries fields; rate-limit hit returns 429 with `Retry-After` + no run; rate-limit clears after the gap elapses; unknown token → 404; inactive endpoint → 403; **paused automation → 409 with audit NOT bumped** (different from schedule); workspace isolation — submitting to one workspace's form doesn't fire automations in another.

No new deps.

Remaining for M9.S1: AI condition trigger (periodic LLM eval — likely defers into M11), Gmail Pub/Sub stub (real in M10). Remaining for M9 overall: M9.S2 (HTTP / Slack / loop action expansion) + M9.S3 (Slack OAuth + post action).

### Revision 10 — 2026-05 — M9.S2 phase 1 + 2 (HTTP + loop actions)

M9.S2 opens. **TC-65 closed.** M9.S2 stays 🏗️ — CRM-mutate expansion + Slack action still open.

- **`crm.http.request`** (phase 1) registered in `apps/automations/actions.py`. Schema: `{url, method?, headers?, body?, auth?, timeout_seconds?, expect_json?}`. URL must be `http://` or `https://` (basic SSRF guard — real DNS-resolution check defers to M11). Method allowlist: GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS. Auth presets: `{type: none}` (default), `{type: bearer, token}` → `Authorization: Bearer ...`, `{type: basic, username, password}` → base64-encoded, `{type: header, name, value}` → arbitrary header. Timeout bounded 1..120s (default 30). dict/list bodies sent as `json=`; string body sent as `content=`. Follows redirects. Response: `{status_code, headers, body}` — `expect_json: true` (default) tries `.json()` and falls back to text; `expect_json: false` always returns text. Response body truncated at **256 KB** with `…[truncated]` suffix to keep `AutomationStepRun.output` bounded. `httpx.RequestError` → `ActionError` so the inspector shows a clean message. Uses `httpx` which was already transitively pulled in by `anthropic==0.42.0`. 15 hermetic tests via `monkeypatch.setattr(httpx.Client, "request", ...)` + a small `FakeResponse` class — captures method/url/headers/json/content + asserts auth-header shape per preset, response decoding, error mapping, validation rejections.
- **`crm.loop`** (phase 2) registered in `apps/automations/actions.py`. Schema: `{items, inner_action, inner_input, max_items?, on_error?}`. Iterates `items` left-to-right, resolves the `inner_input` template against `{item, index}` bindings (strings shaped `{{ item.<dotted.path> }}` or `{{ index }}` or `{{ item }}` resolve; literals pass through; unknown paths return `None`), calls the registered `inner_action`, collects `{index, output}` rows in `results`. `on_error: continue` (default) logs the failing index into `errors[]` and keeps going; `on_error: abort` raises `ActionError`. `max_items` user limit + 5000 hard cap; `inner_action == "crm.loop"` rejected to prevent self-nesting. **Idempotency caveat** documented in the docstring: the whole loop is one `AutomationStepRun`, so a crash mid-loop replays from index 0 — inner actions that mutate external state should dedupe by stable identifier (e.g., email). Per-iteration idempotency keys land with the M11 sub-graph loop. 14 hermetic tests — uses ad-hoc `@register("test.capture.N")` handlers cleaned up in `finally:` so the registry stays uncontaminated; covers iteration order, `{{ item }}` / `{{ index }}` / dotted-path template resolution, nested dict/list templates, empty list short-circuit, `continue` vs `abort` error policies, both max-items caps, all validation rejections (non-list items, missing inner_action, non-dict inner_input, unknown inner action, bad `on_error`), and the self-nest guard.
- **Describe-in-English ergonomics.** Both actions are auto-picked-up by the `automations.author_from_nl.v1` Claude prompt — it interpolates `actions.all_names()` at build time, so the new actions appear in the system prompt's "Available actions" line without any prompt edit needed.

Remaining for M9.S2: CRM mutates for Company / Deal / Task / Note; Slack action (depends on M9.S3); retry/timeout knobs on `crm.loop`'s inner-action errors (or push to a real sub-graph loop in M11).

Remaining for M9 overall: M9.S3 (Slack OAuth in `apps/integrations` + `crm.slack.post_message` action — closes TC-62 + TC-63), **M9.S4 Agents Marketplace v1 (demo-critical, FR-26)**, AI-condition trigger, run-inspector retry counts.

### Revision 11 — 2026-05 — M9.S2 phase 3 (CRM-mutate action expansion)

Seven new CRM-mutate actions land. M9.S2 stays 🏗️ — only Slack action remains.

- **Update actions.** `crm.update_contact`, `crm.update_company`, `crm.update_deal` all take `{<entity>_id, patch}` and route through a new `_apply_patch(instance, patch, allowed, *, action_name)` helper. Each entity has its own `_*_PATCHABLE_FIELDS` set: contact (first_name, last_name, primary_email, phones, title, company_id, owner_id, lifecycle_stage, source, custom, tags), company (name, domain, size_band, industry, owner_id, custom, tags), deal (name, stage_id, value_cents, currency, expected_close, contact_id, company_id, owner_id, custom, tags). Patch keys outside the allowlist raise `ActionError` listing the rejected fields + the allowed set, so tampering with workspace / created_by / created_at / deleted_at is impossible. `_apply_patch` only saves fields whose value actually changed — minimal `update_fields=...` — and returns the list of changed field names for the action's response.
- **Create actions.** `crm.create_company` (validates name + created_by_id), `crm.create_deal` (validates pipeline_id exists in the workspace, and stage_id is in the pipeline's stages array — invalid stage raises with the valid-stages hint), `crm.create_task` (validates `related_type` against the `{contact, company, deal, task, note}` allowlist), `crm.create_note` (validates body_md + related_type allowlist). All return the new row's id + a couple of human-friendly fields so downstream steps can template them as `{{ <node>.<field> }}`.
- **Workspace isolation.** Every update/create scopes by `workspace=workspace, pk=..., deleted_at__isnull=True` so cross-workspace attempts return "not found" — same path as the workspace-isolation guard. Tested explicitly for `crm.update_contact`.
- **Tests.** 17 new in `apps/automations/tests/test_crm_actions.py`. Update-contact: happy path, disallowed-field rejection (including the `workspace_id` tamper attempt), not-found, workspace isolation, no-op patch returns empty `updated_fields`. Create/update company: round-trip + missing-required-field rejections. Create deal: happy path, invalid stage rejection with stages hint, pipeline-not-found. Update deal: allowed-field patch, disallowed `created_at` rejected. Create task: against a contact + bad `related_type` rejection. Create note: against a deal + missing body rejection. Registry test confirms all 7 new names are registered.
- **Describe-in-English ergonomics.** The `automations.author_from_nl.v1` Claude prompt enumerates `actions.all_names()` at build time, so these 7 actions appear in the system prompt automatically — no prompt edits needed. **13 registered actions total** now: `noop`, `log`, `crm.create_contact`, `crm.update_contact`, `crm.create_company`, `crm.update_company`, `crm.create_deal`, `crm.update_deal`, `crm.move_deal_stage`, `crm.create_task`, `crm.create_note`, `crm.http.request`, `crm.loop`.

No new deps. Tests + manual smoke pending the Docker toolchain.

Remaining for M9.S2: Slack action (depends on M9.S3 OAuth). Remaining for M9 overall: M9.S3 (Slack OAuth + post-message) + AI-condition trigger + run-inspector retry counts.

### Revision 12 — 2026-05-13 — M9.S4 Agents Marketplace v1 (FR-26) added

**Demo-critical scope addition.** No code yet — this revision documents the new user story queued for immediate implementation ahead of the conference demo. PRD bumped to v3 (FR-26 added; POST-15 clarified as the third-party-developer successor).

- **New PRD requirement:** FR-26 — Agents Marketplace v1 (P0). Workspace-agnostic curated catalog (4–6 hand-seeded agents) with one-click install that creates an `Automation` + published `AutomationVersion` in the workspace. Installed agents are immediately editable; the marketplace is a starting-point, not a black box.
- **New ROADMAP user story:** M9.S4 under existing Phase M9 — keeps milestone count at 16 (M0–M15) without disturbing downstream numbering.
- **Demo path:** open `/marketplace` → install *Lead qualification* → land in the M8 canvas with v1 published → optionally edit one node → trigger a contact create → see the run in the Inspector with step outputs + cost. Tells the "AI-native CRM with workflows you don't have to build from scratch" story in under 5 minutes.
- **Implementation breakdown (queued — ~3 days):**
  1. **Backend** (~1 day): `apps/marketplace` Django app with `MarketplaceAgent` (slug + name + description + category + icon_emoji + graph + trigger + install_count + author + published_at — workspace-agnostic) and `WorkspaceAgentInstall` (workspace + marketplace_agent FK + automation FK + installed_by + installed_at) models. Migration `0001_initial.py` depending on `automations.0005_formendpoint`. DRF: `MarketplaceAgentViewSet` (read-only list/detail, AllowAny no-auth so catalog is shareable) + `install` @action (manager-gated, workspace-scoped, atomic snapshot into Automation + AutomationVersion + bumps `install_count` via `F("install_count")+1`). Admin registration.
  2. **Seed data** (~0.5 days): `tools/seeds/marketplace.py` with 4–6 agents spanning trigger types — *Lead qualification* (record contact-created → branch on score → crm.create_task), *Deal hygiene sweep* (schedule `0 9 * * MON` → crm.loop over stale deals → crm.update_deal), *Inbound webhook → contact* (webhook trigger → crm.create_contact → crm.create_note), *Stalled-deal nudge* (schedule + crm.http.request → Slack incoming-webhook URL pre-filled). All use only currently-shipped action types.
  3. **Frontend** (~1.5 days): `/[workspace]/marketplace/` grid page with category filter + icon + install_count badge; `/[workspace]/marketplace/{slug}/` detail page with read-only `WorkflowCanvas` (`readOnly` prop already supported) preview + Install button; sidebar entry; `lib/api.ts` hooks (`useMarketplaceAgents`, `useMarketplaceAgent`, `useInstallMarketplaceAgent`); install redirects to `/[workspace]/automations/{id}/`.
  4. **Tests** (~0.5 days): TC-92 catalog anon-readable; TC-93 install round-trip (manager-only, creates Automation + AutomationVersion + WorkspaceAgentInstall + bumps install_count); TC-94 edit-after-install (graph diverges from catalog without affecting other workspaces' installs).
- **Demo prerequisites:** none new. Reuses M7 runtime + M8 canvas/inspector + M9 trigger dispatcher + 13 registered actions. Skip M9.S3 (Slack OAuth) for demo if time-tight — Stalled-deal-nudge agent can use a placeholder Slack URL and the run inspector shows the http step output cleanly without a real Slack workspace.

Recommended implementation order for the demo timeline:
1. **M9.S4 backend + seed** (~1.5 days).
2. **M9.S4 frontend** (~1.5 days).
3. Optional: **M9.S3 Slack OAuth** (~2 days) if time allows — promotes the Stalled-deal-nudge agent from "HTTP to placeholder URL" to "real Slack post."
4. Optional polish: M8 HITL HTTP decide endpoint (~0.5 days) so any HITL-using marketplace agent demos cleanly.

### Revision 13 — 2026-05 — M9.S4 backend + product repositioning around OffsideStudio — Agent Marketplace

Two concurrent changes:

1. **M9.S4 Agents Marketplace backend shipped.** New `apps/marketplace` Django app with `MarketplaceAgent` (workspace-agnostic catalog row: slug, name, description, long_description, category enum, icon_emoji, author, graph, trigger, install_count, is_published, audit) + `WorkspaceAgentInstall` (per-workspace audit FKs the freshly-created `Automation`). Migration `0001_initial.py` (depends on `automations.0005_formendpoint`). DRF: `MarketplaceAgentViewSet` — catalog list/detail with `AllowAny` + no auth (catalog is shareable); `install` `@action` is manager-gated, uses `WorkspaceJWTAuthentication`, atomically snapshots the agent's graph + trigger into a new `Automation`, calls `publish_automation` (flips to ACTIVE + creates v1), writes `WorkspaceAgentInstall` audit row, bumps `install_count` via `F("install_count") + 1`. `__INSTALLER__` sentinel resolution in `_resolve_installer_sentinels` replaces every literal occurrence with the installer's user id so seed graphs are portable across workspaces. Wired into `offside_crm/urls.py` at `/api/marketplace/`. Admin registrations for both models. **M7 runtime tweak (additive):** `run_advancer` now seeds `state_snapshot.trigger = trigger_payload` on the PENDING → RUNNING transition so `{{ trigger.<field> }}` templates resolve in action inputs — unblocks the seed agents. `tools/seeds/marketplace.py` ships 4 hand-curated agents using only currently-shipped triggers + actions (Lead qualification 🎯, Welcome new contact 👋, Deal pulse 🔔, Outbound HTTP ping 🔌). 9 tests in `apps/marketplace/tests/test_marketplace.py` cover TC-92 (catalog anon-readable + list/detail/category-filter + unpublished hidden), TC-93 (install round-trip + workspace-header requirement + manager-role gating + `__INSTALLER__` resolution), TC-94 (edit-after-install isolation from catalog + v1 snapshot immutability), plus re-install creates separate Automation rows.

2. **Product repositioning around "OffsideStudio — Agent Marketplace" as default selling proposition.** PRD bumped to v3.1. The Agents Marketplace (FR-26) is now framed as the ★★ headline surface; the Agent Design Studio (FR-12, renamed from "Workflow node-graph editor") is the ★ companion hero. Both surfaces lead the product's UX hierarchy; CRM record views (FR-3..FR-7) become the data layer underneath. PLAN.md / PRD.md / ROADMAP.md / CLAUDE.md / MEMORY.md / TESTING.md all rewritten at the top to use the new positioning. Frontend implementation deliverables (next slice): sidebar leads with Marketplace + Studio; `/automations` empty state pitches the Marketplace; primary navigation reordered.

Remaining for M9.S4: frontend grid + detail + install button + sidebar Marketplace entry + `lib/api.ts` hooks + manual UI smoke. Backend is ready for the frontend to call.

---

*ROADMAP.md ends.*
