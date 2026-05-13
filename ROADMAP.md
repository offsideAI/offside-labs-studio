# Offside CRM — Roadmap (ROADMAP.md)

> Companion to [PRD.md](./PRD.md) and [PLAN.md](./PLAN.md). Each **phase maps 1:1 to an epic.** Inside an epic, work is broken into user stories (the "what" from a user's view) and engineering tasks (the "how"). Acceptance criteria match the milestone demo defined in PLAN.md §13. Cross-references to PRD `FR-N` / `NFR-N` and TESTING `TC-N` are noted on each phase.

**Status:** M0–M7 shipped + pushed to `origin/main`. M8 — all three user stories (S1 + S2 + S3) shipped locally. M9 — trigger dispatcher + record + webhook + schedule triggers shipped locally; form / AI condition + action expansion + Slack pending. Lingering M8 punch-list: HITL HTTP decide endpoint, undo/redo, TC-29..TC-32 frontend smoke-tests.
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

### `[🏗️]` Phase M8 — Workflow node-graph editor v1 (Epic: Visual Authoring)
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

### `[🏗️]` Phase M9 — Workflow engine completeness (Epic: Triggers, Actions, Integrations)
*Status:* in progress — trigger dispatcher + record + webhook + schedule shipped; form / AI condition + action expansion + Slack pending · *Estimate:* 7 days · *Depends on:* M8 · *Covers:* FR-11 (full), FR-21, FR-22 · *Tests:* TC-39, TC-62–TC-65, TC-83

**User stories**
- `[🏗️]` M9.S1 — As an admin, I can use any of the v1 trigger types (record, time, webhook, form, AI condition). *Phase 1 shipped: `apps/automations/triggers.py` dispatcher (`TriggerEvent` dataclass, `fire(event)` matches by `type` against every ACTIVE+published automation in the workspace, `run_automation_with_payload(...)` for explicitly-routed types). **Record** trigger: Contact / Company / Deal create + Deal `stage_changed` post-save handlers dispatch via `transaction.on_commit` so rollbacks don't fire automations. **Webhook** trigger (phase 2a): `WebhookEndpoint` model + public `POST /api/webhooks/{token}/` view with `X-Offside-Signature` HMAC-SHA256 verification (accepts `sha256=<hex>` or bare hex), unknown-token→404, inactive→403, paused-automation→409, success→200+`{run_id}` + atomic `F("fire_count")+1`. **Schedule** trigger (phase 2b): `ScheduleTrigger` model (cron_expression + timezone_name + is_active + last_fired_at + fire_count) + `automations.scan_schedule_triggers` Beat task running every 60s — parses the 5-field cron via `celery.schedules.crontab` and calls `is_due(last_fired_at or now-61s)`; due rows call `run_automation_with_payload(trigger_type="schedule")`. **No-backlog semantics**: paused/unpublished automations still stamp `last_fired_at` on every sweep so un-pause doesn't fire a backlog. Bad cron strings logged + skipped without poisoning the sweep. 26 new tests total (10 dispatcher + 8 webhook + 8 schedule). **Pending:** form (public unsigned POST), AI condition (periodic LLM eval — likely defers into M11), Gmail Pub/Sub stub (real in M10).*
- `[☑️]` M9.S2 — As an admin, I can use any v1 action type (CRM mutate, Slack, HTTP, branch, loop, delay, approval).
- `[☑️]` M9.S3 — As an admin, I can post to Slack channels/DMs from any workflow.

**Engineering tasks**
- `[🏗️]` Trigger registry — webhook (HMAC), record, and schedule (Beat-driven) shipped (see M9.S1 note above). Form-submission endpoint, AI-condition, Gmail Pub/Sub stub still pending.
- `[☑️]` Action registry expansion — CRM mutations across all M5 entities; Slack action via OAuth integration; HTTP request with auth presets; loop-over-list step. (Branch + delay already in M7.)
- `[☑️]` Slack OAuth + connection model in `apps/integrations`.
- `[☑️]` Run inspector enriched — node graph viewer, retry counts, idempotency keys visible.

**Acceptance criteria**
- `[🏗️]` TC-39 (transient retry — M7 idempotency proven; retry-loop visibility pending), TC-62 (Slack connect — pending), TC-63 (post Slack from workflow — pending), TC-64 (inbound webhook fires workflow — **closed**: webhook endpoint + HMAC verification + tests prove fire-on-valid-sig, no-fire-on-bad-sig, audit counter bump), TC-65 (outbound HTTP with bearer — pending), TC-83 (advancer step latency budget — pending).
- `[☑️]` 10-step workflow with branch + loop + HITL approve-from-iOS-push works end-to-end.

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
| M9  | 7 | `[🏗️]` |
| M10 | 7 | `[☑️]` |
| M11 | 6 | `[☑️]` |
| M12 | 5 | `[☑️]` |
| M13 | 7 | `[☑️]` |
| M14 | 4 | `[☑️]` |
| M15 | 7 | `[☑️]` |
| **Total** | **83 days** | **8 of 16 milestones complete** |

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

---

*ROADMAP.md ends.*
