# Offside CRM — Product Requirements Document (PRD)

> Companion to [PLAN.md](./PLAN.md). PLAN.md captures architecture and engineering decisions; **PRD.md captures product requirements from the user's perspective**. Every functional and non-functional requirement here gets a stable ID (`FR-N`, `NFR-N`) so [ROADMAP.md](./ROADMAP.md) and [TESTING.md](./TESTING.md) can reference them without drift.

**Status:** Draft v2 — checkbox-tracked. M0–M7 shipped; M8 next.
**Product:** Offside CRM (suite product #1 of 4).
**Owner:** Offside Labs.
**Last revised:** 2026-05.

---

## Status legend

- `[✅]` — implemented and on `main`
- `[🏗️]` — partially implemented / in progress
- `[☑️]` — pending (not implemented yet)

Each FR / NFR / POST has a rollup status; user stories and acceptance criteria each get their own checkbox so partial deliveries stay honest. The "Roadmap mapping" line on each FR points at the ROADMAP milestone(s) that ship the work.

---

## 1. Executive summary

Offside CRM is the first product in the Offside Studio Suite, positioned for **SMB sales teams (2–20 reps)**. It fuses a polished record/pipeline experience (HubSpot/Attio lineage), a workflow automation engine (Zapier/n8n lineage), and pervasive AI — under a single coherent UX where AI is a first-class primitive, not a side panel.

The wedge is **"AI everywhere"**: prompt-first workflow authoring on top of a node-graph canvas, conversational data access, comms intelligence on every record, and opt-in autonomous agentic action with human-in-the-loop approval.

---

## 2. Vision & positioning

> "Make HubSpot's CRM core, Zapier's automation flexibility, and Attio's design polish feel old."

Operating principles:
- **AI-native, not AI-adjacent.** Every record view, automation, search, and follow-up is AI-aware.
- **Automation as a peer, not a side panel.** Workflows and CRM records share one mental model and one event bus.
- **Web-first** with native iOS as a peer surface for read/edit + agent approvals on the go.
- **Opinionated UX.** Keyboard-first, command-palette-everywhere, dense-but-calm.
- **The 80–90% of Zapier's automation power**, with a dramatically better authoring experience for AI steps.

Suite positioning: every Offside product (CRM, Crunch, Design, Director) shares voice, brand, and shared infrastructure. Offside is engineer-to-engineer — confident, technical, never breathless.

---

## 3. Personas

### 3.1 Manager — sales lead / owner (`P-1`)
- **Context:** Founder, head of sales, or sales manager at a 2–20 person company.
- **Goals:** Pipeline visibility; team accountability; less time configuring tools, more time selling.
- **Pain points with current CRMs:** Setup is heavy; automations live in a separate tool; AI features are bolt-on.
- **Daily surfaces:** Workspace home / pipeline view, automation builder, agent inbox, reports.

### 3.2 Individual contributor — sales rep (`P-2`)
- **Context:** Account executive or SDR doing outbound + working assigned deals.
- **Goals:** Spend the day on relationships, not data entry; instant follow-ups; never miss a hot deal.
- **Daily surfaces:** Contact + deal records, inbox, command palette, iOS for on-the-go.

### 3.3 Admin / RevOps (`P-3`)
- **Context:** Configures pipelines, custom fields, integrations, agent policies. Often the manager wearing this hat in early-stage SMBs.
- **Goals:** Sane defaults that customize without breaking; safe rollout of agent autonomy.
- **Daily surfaces:** Settings, automation library, agent policy table, audit logs.

### 3.4 Read-only viewer (`P-4`)
- **Context:** Executive, investor, or cross-functional partner who needs to see the pipeline without editing.
- **Goals:** Glance at the funnel; drill into specific deals.
- **Daily surfaces:** Dashboards, saved views.

---

## 4. Functional requirements

Every FR has: **Status** · **ID** · **Priority** (P0 = MVP, P1 = post-MVP) · **Roadmap mapping** · **Personas affected** · **Description** · **User stories** · **Acceptance criteria**.

### `[✅]` FR-1 — Workspaces & multi-tenancy (PLAN §6)
- **Priority:** P0 · **Personas:** P-1, P-3 · **Roadmap:** M2 (✅)
- **Description:** Every account creates or joins a workspace. All data is workspace-scoped. Roles: `owner`, `admin`, `manager`, `rep`, `read-only`.
- **User stories:**
  - `[✅]` As a manager, I can create a new workspace and invite up to 19 teammates. *(M2.S1, M2.S2)*
  - `[✅]` As an admin, I can change a teammate's role. *(implemented in M3 settings page; TC-6)*
  - `[✅]` As a rep, I can switch between workspaces I belong to without logging out. *(M2.S3)*
- **Acceptance criteria:**
  - `[✅]` Workspace switcher reachable in ≤2 keystrokes from anywhere in the app.
  - `[✅]` Backend rejects any cross-workspace data access with 403.
  - `[✅]` Invite flow uses Resend magic-link; invitee lands on signup → workspace auto-joined.

### `[✅]` FR-2 — Auth & user management (PLAN §5)
- **Priority:** P0 · **Personas:** P-1, P-2, P-3, P-4 · **Roadmap:** M1 (✅)
- **Description:** Email-based signup/login with JWT (access 1d / refresh 14d). allauth + dj-rest-auth + SimpleJWT on the backend. Password reset, email verification, JWT refresh-on-401.
- **User stories:**
  - `[✅]` As a new user, I can sign up with email + password. *(M1.S1)*
  - `[✅]` As a returning user, I can log in on web and iOS with the same credentials and stay logged in. *(M2 web, M6 iOS)*
  - `[✅]` As a user, I can reset a forgotten password via email link.
- **Acceptance criteria:**
  - `[✅]` Signup → workspace creation flow ≤30 seconds.
  - `[✅]` Refresh token rotation; access token revoked on logout.
  - `[✅]` iOS Keychain stores tokens; web stores refresh in HTTP-only cookie.

### `[✅]` FR-3 — Contacts (PLAN §6)
- **Priority:** P0 · **Personas:** P-2, P-3 · **Roadmap:** M4 (✅) web; M6 (✅) iOS read-only
- **Description:** First/last name, primary email, phone(s), title, company FK, owner FK, lifecycle stage, source, custom fields.
- **User stories:**
  - `[✅]` As a rep, I can create, view, edit, and archive a contact. *(M4.S1)*
  - `[✅]` As a rep, I can search contacts by name, email, or any custom field. *(M4.S4 via filter DSL; full FTS in M12)*
  - `[✅]` As an admin, I can define custom fields per workspace. *(M4.S3, FR-8)*
- **Acceptance criteria:**
  - `[🏗️]` List view paginates 1k contacts smoothly (≤200ms after filter change). *(Pagination works; perf budget verified in M15.)*
  - `[✅]` Detail view shows the full activity timeline. *(M5 ActivityFeed)*
  - `[✅]` Soft-delete via archive (recoverable for 90 days).

### `[✅]` FR-4 — Companies (PLAN §6)
- **Priority:** P0 · **Personas:** P-2, P-3 · **Roadmap:** M4 (✅) web; M6 (✅) iOS read-only
- **Description:** Name, domain, size band, industry, owner FK, custom fields. Many-to-one with contacts.
- **User stories:**
  - `[✅]` As a rep, I can view all contacts associated with a company.
  - `[✅]` As a rep, I can navigate to a deal directly from a company page. *(TC-13 via M5 link)*
- **Acceptance criteria:**
  - `[✅]` Domain auto-uniqueness check on create. *(per-workspace unique constraint on non-empty domain)*
  - `[☑️]` Company merge flagged in P1 (POST-MVP).

### `[✅]` FR-5 — Deals & pipelines (PLAN §6)
- **Priority:** P0 · **Personas:** P-1, P-2 · **Roadmap:** M5 (✅) web; M6 (✅) iOS read-only
- **Description:** Deal name, value, currency, stage, pipeline, owner, expected close, contact + company FKs, custom fields. Workspace-defined pipelines with ordered stages.
- **User stories:**
  - `[✅]` As a manager, I can create a pipeline and order its stages. *(M5.S1)*
  - `[✅]` As a rep, I can drag a deal across stages on a kanban view. *(M5.S2 — DnD-kit)*
  - `[☑️]` As a manager, I can switch a pipeline view to a list view. *(Kanban-only today; list view post-M14.)*
- **Acceptance criteria:**
  - `[✅]` Stage change emits an `activity` row + a `record_field_changed` automation event. *(M5 signal handler)*
  - `[✅]` Currency stored in cents; display localized. *(value_cents Int + Intl formatter)*

### `[🏗️]` FR-6 — Tasks (PLAN §6)
- **Priority:** P0 · **Personas:** P-1, P-2 · **Roadmap:** M5 (✅) web; M13 (☑️) iOS tasks tab
- **Description:** Title, due, owner, polymorphic relation (contact/company/deal), status, priority, custom fields.
- **User stories:**
  - `[✅]` As a rep, I can create a task on any record from its detail view. *(M5 TasksTab)*
  - `[☑️]` As a rep, I see today's tasks in a "today" smart view. *(Per-record view today; global today list lands at M14.)*
- **Acceptance criteria:**
  - `[✅]` Overdue tasks highlight in tan-text accent. *(M5 TasksTab CSS)*
  - `[✅]` Tasks scoped per workspace. *(WorkspaceScopedManager)*

### `[✅]` FR-7 — Notes & activities (PLAN §6)
- **Priority:** P0 · **Personas:** P-2 · **Roadmap:** M5 (✅)
- **Description:** Notes are Markdown bodies attached to records. Activities are append-only event rows: emails, calls, meetings, AI actions, automation runs, field changes.
- **User stories:**
  - `[✅]` As a rep, I can add a note to a contact and edit it within 24 hours. *(M5 NotesTab + 24h edit window)*
  - `[✅]` As a rep, I see a chronological activity feed on every record. *(M5 ActivityFeed)*
- **Acceptance criteria:**
  - `[🏗️]` Activity feed paginates infinite scroll. *(Server pagination ready; UI uses default page size today, scroll wired in M14.)*
  - `[✅]` Note edits beyond 24h create an audit trail. *(`edit_log` JSONB + view-level enforcement)*

### `[✅]` FR-8 — Custom fields (PLAN §6)
- **Priority:** P0 · **Personas:** P-3 · **Roadmap:** M4 (✅)
- **Description:** Per-workspace, per-entity custom field definitions. Types: `text`, `long_text`, `number`, `select`, `multi_select`, `date`, `datetime`, `boolean`, `url`, `email`, `phone`, `relation`.
- **User stories:**
  - `[✅]` As an admin, I can add a custom field "Lead Score" of type `number` to contacts.
  - `[✅]` As a rep, I can filter and sort by custom fields. *(filter DSL with `custom.<key>` paths)*
- **Acceptance criteria:**
  - `[✅]` Adding a field doesn't require a schema migration (JSONB-backed).
  - `[☑️]` Hot fields can be promoted to indexed expression columns by an admin. *(Post-MVP shortcut: a single `index_now` flag.)*

### `[☑️]` FR-9 — Email sync (Gmail) (PLAN §4.4)
- **Priority:** P0 · **Personas:** P-2 · **Roadmap:** M10 (☑️)
- **Description:** OAuth-connect a Gmail account. Sync threads + messages to/from contacts. Send mail from inside Offside as the connected user.
- **User stories:**
  - `[☑️]` As a rep, I can connect my Gmail and see threads with each contact.
  - `[☑️]` As a rep, I can send an email to a contact from inside the contact view.
  - `[☑️]` As a rep, I receive in-app activity when a contact replies.
- **Acceptance criteria:**
  - `[☑️]` Initial sync ingests last 90 days; ongoing sync is real-time via Pub/Sub push.
  - `[☑️]` Disconnect revokes tokens server-side.

### `[☑️]` FR-10 — Calendar sync (Google Calendar) (PLAN §4.4)
- **Priority:** P0 · **Personas:** P-1, P-2 · **Roadmap:** M10 (☑️)
- **Description:** OAuth-connect Google Calendar. Sync events to record activity timelines and trigger automations.
- **User stories:**
  - `[☑️]` As a rep, I see my upcoming meetings on each contact/deal record.
  - `[☑️]` As a rep, I can create a calendar event from a contact (auto-invite the contact).
- **Acceptance criteria:**
  - `[☑️]` Past meeting summaries (FR-13) appear within 30s of the meeting ending.

### `[🏗️]` FR-11 — Workflow automation engine (PLAN §7)
- **Priority:** P0 · **Personas:** P-1, P-3 · **Roadmap:** M7 (✅) foundation; M8 (☑️) editor; M9 (☑️) full triggers/actions
- **Description:** Durable, idempotent workflow runtime built on Celery + Postgres + custom Django layer. Triggers (record events, time, webhook, form, email-received, AI-condition), actions (CRM mutations, comms, logic, AI, HTTP), HITL approval, retries, run inspection.
- **User stories:**
  - `[🏗️]` As an admin, I can build a workflow that triggers on "deal moved to Negotiation" and waits 1 day before drafting an AI follow-up email. *(Runtime can execute; visual authoring + AI step handler land in M8 + M11.)*
  - `[☑️]` As a rep, I see workflow runs in a per-record activity feed. *(Activity log exists; automation_run signal hook lands with the editor in M8.)*
  - `[☑️]` As an admin, I can replay or cancel a stuck run. *(Django admin shows runs; UI controls in M8.)*
- **Acceptance criteria:**
  - `[✅]` Worker restart mid-run does not lose state (idempotency + persisted state_snapshot). *(M7 chaos test)*
  - `[✅]` HITL approval token signed and single-use; expires in 7 days. *(M7 hitl.py)*
  - `[✅]` Run inspector shows step-by-step input/output/cost/latency. *(M7 Django admin)*

### `[☑️]` FR-12 — Workflow node-graph editor (PLAN §7.2)
- **Priority:** P0 · **Personas:** P-1, P-3 · **Roadmap:** M8 (☑️)
- **Description:** Pure node-graph canvas (React Flow) with node palette. Optional "Describe in English" panel that hydrates a graph from natural language.
- **User stories:**
  - `[☑️]` As an admin, I can drag nodes onto the canvas and connect them with edges.
  - `[☑️]` As an admin, I can save a draft and publish it as a new version.
  - `[☑️]` As an admin, I can describe a workflow in English and let Claude generate the node graph.
- **Acceptance criteria:**
  - `[☑️]` Canvas renders 100-node workflows without jank.
  - `[☑️]` Undo/redo for canvas edits.
  - `[☑️]` Schema validation prevents publishing a malformed graph.

### `[☑️]` FR-13 — AI: comms intelligence (PLAN §8.4)
- **Priority:** P0 · **Personas:** P-2 · **Roadmap:** M11 (☑️)
- **Description:** Streaming AI drafts, reply suggestions, thread summaries, meeting summaries. Surfaced in every contact + deal view.
- **User stories:**
  - `[☑️]` As a rep, I can ask AI to draft a follow-up email for this contact based on our last 3 messages + deal stage.
  - `[☑️]` As a rep, I can read a 3-bullet summary of a long Gmail thread.
  - `[☑️]` As a rep, after a Google Calendar meeting, I can paste the transcript and get a 5-bullet summary written to the deal's activity log.
- **Acceptance criteria:**
  - `[☑️]` First token of a draft arrives ≤1.5s P95.
  - `[☑️]` Drafts are editable in-place before send.
  - `[☑️]` Cost shown per generation in admin telemetry.

### `[☑️]` FR-14 — AI: NL data layer (PLAN §8.2)
- **Priority:** P0 · **Personas:** P-1, P-2 · **Roadmap:** M12 (☑️)
- **Description:** Natural-language queries → structured filter DSL → server-side query → results + AI summary.
- **User stories:**
  - `[☑️]` As a manager, I can type "deals over $10k that went quiet last week" into cmd-K and see a filtered list.
  - `[☑️]` As a rep, I can save the resulting filter as a saved view.
- **Acceptance criteria:**
  - `[☑️]` NL → filter DSL conversion ≤2s P95.
  - `[☑️]` Hybrid search (FTS + pgvector rerank) for fuzzy queries.
  - `[☑️]` Schema-aware prompting: includes custom fields.

### `[☑️]` FR-15 — AI: lead scoring + enrichment (PLAN §8.3)
- **Priority:** P0 · **Personas:** P-2, P-3 · **Roadmap:** M11 (☑️)
- **Description:** Background workers populate lead score + company enrichment fields on new contacts/companies.
- **User stories:**
  - `[☑️]` As a rep, when I add a contact with email `john@stripe.com`, I see Stripe's company size and industry auto-fill within 60s.
  - `[☑️]` As an admin, I can disable enrichment per workspace.
- **Acceptance criteria:**
  - `[☑️]` Per-workspace daily token budget enforced; over-budget → enqueue + notify owner.
  - `[☑️]` Manual "re-score" button on each contact.

### `[☑️]` FR-16 — AI: suggested next actions (PLAN §8)
- **Priority:** P0 · **Personas:** P-2 · **Roadmap:** M11 (☑️)
- **Description:** Per-record AI suggestion strip. Calm, non-chatbot UX.
- **User stories:**
  - `[☑️]` As a rep, on a quiet deal I see "This deal hasn't moved in 5 days — draft a re-engage email?".
  - `[☑️]` As a rep, I can dismiss a suggestion or convert it into a task or workflow.
- **Acceptance criteria:**
  - `[☑️]` Max 3 suggestions visible at once; rest in an overflow.
  - `[☑️]` Dismissed suggestions do not reappear for 7 days.

### `[🏗️]` FR-17 — AI: agent autonomy + HITL (PLAN §8.5)
- **Priority:** P0 · **Personas:** P-1, P-3 · **Roadmap:** M7 (✅) HITL primitive; M13 (☑️) agent loop + UI
- **Description:** Per-workspace action-mode policy table (`suggest` | `approve` | `autonomous`). HITL via in-app inbox + email magic-link + iOS push.
- **User stories:**
  - `[🏗️]` As an admin, I can set "send email to lead" to require approval but "post Slack notification" to be autonomous. *(`AgentPolicy` model + enums in M7; policy UI in M13.)*
  - `[☑️]` As a rep, I can toggle "Agent assist" on a specific deal. *(M13)*
  - `[☑️]` As a rep, I receive an iOS push when an agent action needs my approval; I can approve/reject without opening the app fully. *(M13)*
- **Acceptance criteria:**
  - `[☑️]` Reversible actions (notes, drafts) get a 60-second undo affordance after autonomous execution.
  - `[☑️]` Irreversible actions (sent emails, charged payments — post-MVP) always require approval.
  - `[🏗️]` Audit log records prompt, model, cost, output, decision, decider. *(`AutomationStepRun` columns ✅; agent-action audit row in M13.)*

### `[☑️]` FR-18 — Reports & dashboards (PLAN §13 M14)
- **Priority:** P0 (light) · **Personas:** P-1, P-4 · **Roadmap:** M14 (☑️)
- **Description:** Saved-view counters + simple deal funnel + activity-over-time chart.
- **User stories:**
  - `[☑️]` As a manager, on workspace home I see this week's pipeline + the team's activity.
  - `[☑️]` As a viewer, I can drill from a counter into the underlying records.
- **Acceptance criteria:**
  - `[☑️]` Workspace home loads ≤500ms P95 with cached aggregates.
  - `[☑️]` Charts respect WCAG 2.2 AA (color is not the sole signal).

### `[🏗️]` FR-19 — Search (FTS + pgvector) (PLAN §8.2, §13 M12)
- **Priority:** P0 · **Personas:** P-2 · **Roadmap:** M3 (✅) cmd-K skeleton; M4 (✅) filter DSL; M12 (☑️) FTS + vector
- **Description:** Global cmd-K with FTS + AI-summarized results. Hybrid keyword + vector for fuzzy queries.
- **User stories:**
  - `[🏗️]` As a rep, I can search across contacts, companies, deals, notes, emails from one input. *(Cmd-K palette navigates today; record search lands in M12.)*
  - `[☑️]` As a rep, my recent searches are remembered. *(M12)*
- **Acceptance criteria:**
  - `[✅]` Cmd-K opens in ≤80ms.
  - `[☑️]` First results render ≤200ms after 3 chars. *(Real search results land in M12.)*

### `[🏗️]` FR-20 — Import (CSV, HubSpot, Pipedrive) (PLAN §4.4)
- **Priority:** P0 (CSV) / P1 (HubSpot, Pipedrive) · **Personas:** P-3 · **Roadmap:** M4 (✅) CSV; M11 (☑️) Claude column mapping; POST-2 (☑️) HubSpot/Pipedrive
- **Description:** Switching-cost killer: bring your data in 5 minutes.
- **User stories:**
  - `[☑️]` As an admin, I can paste a HubSpot export URL and have contacts/companies/deals mapped automatically. *(POST-2)*
  - `[✅]` As an admin, I can review and adjust the mapping before committing. *(M4 ImportWizard)*
  - `[✅]` As an admin, I can import a CSV with up to 50k rows. *(supported via Celery streaming task; load tested in M15)*
- **Acceptance criteria:**
  - `[🏗️]` Mapping suggestions powered by AI; user-correctable. *(Heuristic mapper ✅ in M4; Claude prompt `imports.suggest_column_mapping.v1` upgrades it in M11.)*
  - `[✅]` Import runs as a workflow with progress + error report. *(`ImportRun` model + 1.5s-poll wizard)*

### `[☑️]` FR-21 — Slack integration (PLAN §4.4)
- **Priority:** P0 · **Personas:** P-1, P-3 · **Roadmap:** M9 (☑️)
- **Description:** OAuth-connect a Slack workspace. Workflow action: post to channel/DM. In-app notifications also routable to Slack.
- **User stories:**
  - `[☑️]` As an admin, I connect Slack and choose channels for different notification types.
  - `[☑️]` As a rep, I see workflow output in #sales when configured.
- **Acceptance criteria:**
  - `[☑️]` Disconnect revokes tokens; existing workflow steps that point at Slack pause until reconnected.

### `[☑️]` FR-22 — Generic webhooks + HTTP requests (PLAN §4.4)
- **Priority:** P0 · **Personas:** P-3 · **Roadmap:** M9 (☑️)
- **Description:** Inbound webhook endpoints (per-workspace HMAC) and outbound HTTP step for workflows.
- **User stories:**
  - `[☑️]` As an admin, I can copy a unique webhook URL and POST data to it from any system.
  - `[☑️]` As an admin, I can add an HTTP request step in a workflow with custom headers + auth.
- **Acceptance criteria:**
  - `[☑️]` Webhook payloads logged for 7 days for debugging.
  - `[☑️]` HTTP step supports basic + bearer + custom-header auth presets.

### `[🏗️]` FR-23 — Native iOS app (PLAN §4.7)
- **Priority:** P0 · **Personas:** P-1, P-2 · **Roadmap:** M6 (✅) read-only shell; M13 (☑️) full edit + push
- **Description:** SwiftUI app with full read+edit on contacts/deals, push notifications, HITL approval surface.
- **User stories:**
  - `[🏗️]` As a rep, I can sign in on iPhone, browse my pipeline, and edit a deal. *(Sign-in + browse ✅ in M6; edit lands in M13.)*
  - `[☑️]` As a manager, I receive an APNs push when an agent action needs approval; I can approve/reject from the lock screen action. *(M13)*
- **Acceptance criteria:**
  - `[✅]` App launches to "today" view ≤2s on a 3-year-old iPhone. *(M6 cold start)*
  - `[☑️]` Offline read for last 50 visited records; edits queue and sync on reconnect. *(M13 + M15 polish)*
  - `[☑️]` App Store review checklist locally green. *(M15 + TestFlight)*

### `[🏗️]` FR-24 — Notifications (in-app, email, iOS push) (PLAN §4.6)
- **Priority:** P0 · **Personas:** P-1, P-2, P-3 · **Roadmap:** M2 (✅) Resend invites; M13 (☑️) in-app + iOS push
- **Description:** In-app inbox + email (Resend) + iOS push (APNs). User-controlled per-channel preferences.
- **User stories:**
  - `[☑️]` As a rep, I can disable email for `task_due_soon` while keeping push on. *(M13)*
  - `[☑️]` As an admin, I can see which notifications were sent in the last 7 days. *(M13)*
- **Acceptance criteria:**
  - `[☑️]` Quiet hours per user (no push between 9pm–7am local by default).
  - `[☑️]` HITL approval pushes always bypass quiet hours.

### `[🏗️]` FR-25 — Audit logs (light) (PLAN §8.5)
- **Priority:** P0 · **Personas:** P-3 · **Roadmap:** M5 (✅) Activity model + signals; M14 (☑️) admin UI + CSV export
- **Description:** Append-only `activity` rows already cover most actions; admin UI surfaces a filterable log.
- **User stories:**
  - `[🏗️]` As an admin, I can see who changed which deal stage in the last 30 days. *(Data exists in `Activity` table from M5; filter UI lands in M14.)*
  - `[☑️]` As an admin, I can export an audit slice as CSV. *(M14)*
- **Acceptance criteria:**
  - `[✅]` 90-day retention in MVP; longer retention is post-MVP enterprise (POST-5).

---

## 5. Non-functional requirements

NFRs are quality bars rather than discrete deliverables. Most are partially in place from day one and tighten as the project matures; M15 polish formalizes the CI gates.

### `[🏗️]` NFR-1 — Performance
*Roadmap:* M3 (✅) cmd-K open ≤80ms; M15 (☑️) full P95 budget enforcement
- `[✅]` Cmd-K open ≤80ms.
- `[☑️]` First results ≤200ms after 3 chars. *(M12)*
- `[🏗️]` Page-to-page nav P95 ≤300ms (RSC + cached data). *(Working today; CI budget in M15.)*
- `[☑️]` AI streaming: first token P95 ≤1.5s. *(M11)*
- `[✅]` iOS app cold start P95 ≤2s on 3-year-old hardware.
- `[✅]` Workflow advancer step latency P95 ≤500ms (excluding intentional waits/AI). *(M7)*

### `[🏗️]` NFR-2 — Accessibility (WCAG 2.2 AA)
*Roadmap:* M3 (✅) keyboard + skip link + reduced motion; M15 (☑️) axe CI + screen reader pass
- `[✅]` Keyboard navigation across every flow (cmd-K, j/k, slash, esc). *(`j/k` row nav lands with M4 list views and is in place.)*
- `[✅]` `prefers-reduced-motion` collapses all animations.
- `[✅]` Focus-visible ring on every interactive element (tan, 2px, 2px offset).
- `[✅]` Color is never the sole signal (status pills include label text + tone).
- `[✅]` Skip link on every page.
- `[☑️]` Axe-clean on all top-level routes; manual screen-reader pass before each release. *(M15)*

### `[✅]` NFR-3 — Security
*Roadmap:* M1 (✅) auth + HMAC plumbing; M2 (✅) tenant isolation
- `[✅]` All endpoints require JWT except `/auth/*` and `/health`.
- `[✅]` Tenant isolation enforced at the ORM layer (`WorkspaceScopedManager`) + verified by tests.
- `[✅]` Secrets never logged; Sentry scrubs PII.
- `[☑️]` All OAuth tokens encrypted at rest with a workspace-scoped key. *(Lands with M9 Slack + M10 Gmail.)*
- `[✅]` HMAC on inbound webhooks; signed approval tokens for HITL (single-use, 7-day TTL). *(HITL ✅ in M7; webhook HMAC in M9.)*
- `[☑️]` Rate limiting on auth + AI endpoints. *(allauth has rate-limits; AI endpoints rate-limited at M11.)*

### `[🏗️]` NFR-4 — Observability
*Roadmap:* M0 (✅) Sentry config; M11 (☑️) AI telemetry
- `[✅]` Sentry on web + iOS + Django + Celery worker. *(SDKs wired; DSN env var.)*
- `[🏗️]` Structured logs with correlation IDs (request id, workspace id, user id). *(workspace_id in JWT auth; full correlation in M9.)*
- `[☑️]` Per-AI-call telemetry: prompt name, model, tokens, cost, latency. *(M11)*
- `[✅]` Run inspector for every workflow run with full step trace. *(M7 Django admin)*

### `[✅]` NFR-5 — Brand fidelity
*Roadmap:* M0 (✅) tokens + components shipped; enforced in every subsequent milestone
- `[✅]` All UI surfaces consume `packages/ui` tokens. No bespoke colors or fonts.
- `[✅]` Saturated blue/purple/cyan never appears. Tan is emphasis, never fill.
- `[✅]` Light-first; dark surfaces are scoped per section, never global.
- `[✅]` Voice is engineer-to-engineer; no breathless adjective stacking.

### `[☑️]` NFR-6 — Cost guardrails
*Roadmap:* M11 (☑️)
- `[☑️]` Per-workspace daily AI token budget; over-budget → enqueue + admin notification.
- `[☑️]` Provider fallback (Claude → OpenAI/Gemini) on outage or cost spike.
- `[☑️]` Anthropic prompt caching for system prompts and large reference docs.
- `[☑️]` Embeddings written async, batched, deduped by content hash.

### `[🏗️]` NFR-7 — Reliability
*Roadmap:* M7 (✅) idempotency + advancer guarantees; M15 backups
- `[✅]` Worker restart preserves all in-flight workflow runs. *(M7 chaos test)*
- `[✅]` Idempotency keys on every workflow side effect.
- `[☑️]` Backups: managed Postgres point-in-time recovery; nightly logical dump to object storage. *(Configured at first deploy, M15.)*
- `[✅]` Beat wake-up sweep tolerates 60s jitter for delays/waits in MVP.

### `[🏗️]` NFR-8 — Privacy
*Roadmap:* M2 (✅) workspace isolation; M15 (☑️) right-to-delete
- `[✅]` All data is workspace-scoped. No cross-workspace leakage.
- `[☑️]` AI prompts never leak data from one workspace into another's context. *(Cache keys workspace-scoped at M11.)*
- `[☑️]` Right-to-delete: workspace owner can request a hard delete that cascades within 30 days. *(M15 polish + POST-5 retention controls.)*

---

## 6. Constraints

- **Stack:** Next.js 15 (Vercel) + Django 4.2 + DRF + Celery 5 + Redis + Postgres 16 + pgvector + SwiftUI iOS 17+.
- **Hosting:** Vercel (web) + Digital Ocean App Platform (Django web/worker/beat) + DO Managed Postgres + DO Managed Redis.
- **AI:** Anthropic Claude as default; OpenAI/Gemini fallback. No other providers in MVP.
- **Brand:** OffsideAI Design System v1.0 is authoritative; production CSS at `OffsideLabs-AI/offsidelabs-ai-web/assets/css/tailwind.css`.
- **Compliance:** No GDPR/HIPAA/SOC2 for MVP. Right-to-delete (NFR-8) only.
- **Browser support:** Last 2 stable versions of Chrome, Safari, Firefox, Edge. No IE.
- **iOS:** iOS 17+, iPhone only in MVP (iPad post-MVP).

---

## 7. Success metrics (post-launch hypotheses to validate)

| Metric | Target (3 months post-launch) |
|---|---|
| Time-to-first-workflow-published | ≤15 minutes from signup |
| Daily active reps per workspace | ≥60% of provisioned seats |
| AI feature adoption (any AI surface used in last 7 days) | ≥80% of active reps |
| Workflow runs per workspace per week | ≥50 |
| HITL approval rate (approve / total) | ≥90% (proxies "agent suggestions are good") |
| iOS WAU as % of total WAU | ≥35% |
| Workspace 30-day retention | ≥70% |
| Switch-from-other-CRM share (qualitative interviews) | ≥30% mention HubSpot/Pipedrive/Attio as prior tool |

---

## 8. Out of scope (post-MVP placeholders)

> Placeholders deliberately enumerated so we do not redebate in MVP scope reviews. Real prioritization happens after launch + first cohort of users.

### `[☑️]` POST-1 — Stripe / billing (PLAN §14)
- Subscription plans, seat-based pricing, per-workspace metering for AI tokens, free trial, usage caps, dunning.

### `[☑️]` POST-2 — Long-tail integrations
- HubSpot full bidirectional sync, Pipedrive sync, Salesforce, Linear, Notion, Microsoft 365 (Outlook + Teams + OneDrive), Zoom, Twilio (SMS/calls), DocuSign, Stripe (as a CRM data source). Pattern: each is its own connector + workflow trigger/action set.

### `[☑️]` POST-3 — Multi-language i18n (web + iOS)
- Localization framework, translation pipeline, RTL support evaluation.

### `[☑️]` POST-4 — Native Android app
- Kotlin Multiplatform vs native Android Compose decision deferred.

### `[☑️]` POST-5 — Enterprise (SSO/SCIM, audit retention, custom roles, sandbox)
- WorkOS or built-in SAML/OIDC, SCIM provisioning, 7-year audit retention, custom role builder, per-workspace sandbox environments.

### `[☑️]` POST-6 — Suite app: Crunch (AI-native spreadsheet)
- Separate product. Shares `packages/ui` + `packages/ai` + `packages/auth-utils`. Distinct backend.

### `[☑️]` POST-7 — Suite app: Design (AI-native app design tool)
- Separate product. Same shared-package philosophy.

### `[☑️]` POST-8 — Suite app: Director (AI-native marketing suite)
- Separate product. Same shared-package philosophy.

### `[☑️]` POST-9 — Advanced agent capabilities
- Multi-step planning across many records, agent-to-agent handoff, autonomous prospecting from public data, voice-call agents.

### `[☑️]` POST-10 — Workflow advanced features
- Sub-workflows (call workflow A from workflow B), parallel fan-out + join, durable workflow versioning beyond MVP "publish new version" semantics, conditional rollout (10% of records first), workflow templates marketplace.

### `[☑️]` POST-11 — Reporting v2
- Custom dashboards builder, scheduled report email, BI-quality drill-downs, exportable CSV/Excel, formula fields, lookup fields.

### `[☑️]` POST-12 — Mobile features
- iPad layout, Apple Watch complications, Mac Catalyst, offline-first edits with conflict resolution, full-text search on-device.

### `[☑️]` POST-13 — Compliance & data residency
- SOC2 Type 2, ISO 27001, GDPR DPA, regional data residency (EU, APAC), HIPAA where vertical-relevant.

### `[☑️]` POST-14 — Public API + developer portal
- Rate-limited per-workspace API tokens, public OpenAPI spec, sample SDKs, developer docs site.

### `[☑️]` POST-15 — Marketplace + extensions
- Custom workflow nodes contributed by partners, workspace-installable AI prompts, branded automation templates.

---

## 9. Open product questions

- **Pricing model.** Per-seat? Per-workflow-run? Per-AI-token? Hybrid? Default hypothesis: per-seat with AI-token soft caps.
- **Free tier shape.** Time-limited trial vs forever-free with limits?
- **Target wedge customer.** SMB sales (locked) but which sub-segment first? B2B SaaS sales is the most likely beachhead given AI-native fit; agencies are second.
- **Onboarding sequence.** Empty workspace → guided import → guided first workflow? Or "magic" pre-built starter workspaces per industry?
- **Public marketing site.** Reuse `OffsideLabs-AI/offsidelabs-ai-web` content? Net-new copy? Decision affects launch timing.

---

## 10. Document conventions

- **FR-N / NFR-N / POST-N** are stable identifiers. Renumber only by appending; never reuse a retired ID.
- All linked artifacts: [PLAN.md](./PLAN.md), [TESTING.md](./TESTING.md), [ROADMAP.md](./ROADMAP.md).
- This PRD lives at HEAD on `main`. Substantive changes get a "v2 / v3 …" header bump.
- Status checkboxes: `[✅]` implemented, `[🏗️]` partial, `[☑️]` pending — must stay in sync with ROADMAP.md.

---

### Revision history

- **v1 — 2026-05** — initial PRD shipped alongside PLAN.md / TESTING.md / ROADMAP.md.
- **v2 — 2026-05** — added `[✅]/[🏗️]/[☑️]` status checkboxes on every FR / NFR / user story / acceptance criterion. Added "Roadmap mapping" lines so each requirement points at the milestone(s) that ship it. Aligned with ROADMAP.md Revision 2 (M0–M7 complete).

---

*PRD.md ends.*
