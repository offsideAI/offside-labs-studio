# OffsideStudio — Agent Marketplace — End-to-End Test Cases (TESTING.md)

> User-perspective end-to-end test scenarios for **OffsideStudio — Agent Marketplace**. Each case is written as steps a real user would perform, not as a unit test. IDs are stable (`TC-N`); cross-references to [PRD.md](./PRD.md) functional requirements are noted as `FR-N`.
>
> **Hero-surface TCs** for demo coverage: TC-29..TC-32 (Agent Design Studio, FR-12) and TC-92..TC-94 (Agents Marketplace, FR-26). The rest are foundational.

**Purpose:** acceptance gate for milestones, manual QA scripts, and the source list for automated E2E coverage (Playwright on web; XCUITest on iOS).
**Owner:** Offside Labs.
**Last revised:** 2026-05.

---

## Format

Each test case is structured as:

> **`TC-N` Title**
> *Persona:* `P-x` · *Covers:* `FR-N`, `NFR-N` · *Surface:* web / iOS / API
> *Pre-conditions:* what must be true before starting.
> *Steps:* numbered user actions.
> *Expected:* observable outcome.
> *Edge:* notable variations / failure modes.

Severity tags on edges: `[blocking]` = test fails; `[degraded]` = soft-failure / warning.

---

## 1. Auth & Onboarding

### TC-1 New user signs up + creates first workspace
*Persona:* P-1 · *Covers:* FR-1, FR-2 · *Surface:* web
*Pre-conditions:* Fresh email, no existing account.
*Steps:*
1. Navigate to `app.offside.ai/signup`.
2. Enter email + password (≥10 chars, mixed case + digit).
3. Submit form.
4. Receive verification email; click link.
5. Land on workspace-creation form; enter workspace name "Acme Sales".
6. Submit; auto-navigate to workspace home.
*Expected:* Authenticated session; workspace created with the user as `owner`; brand-tan welcome banner with the workspace name; activity log empty.
*Edge:* `[blocking]` Reused email → 409 with link to login. `[degraded]` Verification link expired → resend flow.

### TC-2 Returning user logs in via web
*Persona:* P-2 · *Covers:* FR-2 · *Surface:* web
*Pre-conditions:* Existing verified account.
*Steps:*
1. Navigate to `app.offside.ai/login`.
2. Enter email + password.
3. Submit.
*Expected:* Redirect to last-visited workspace + last-visited route. JWT stored in HTTP-only cookie + access in memory.
*Edge:* `[blocking]` Wrong password → 401, no email enumeration; rate-limited after 5 attempts.

### TC-3 User resets forgotten password
*Persona:* P-2 · *Covers:* FR-2 · *Surface:* web
*Pre-conditions:* Existing account.
*Steps:*
1. Click "Forgot password" on login.
2. Enter email; submit.
3. Receive reset email; click link.
4. Set new password; submit.
*Expected:* New password works; old refresh tokens revoked.
*Edge:* `[blocking]` Reset token expired (>1h) → "Request a new link" message.

### TC-4 User logs out cleanly
*Persona:* P-2 · *Covers:* FR-2 · *Surface:* web + iOS
*Pre-conditions:* Logged in.
*Steps:*
1. Click avatar → "Log out".
*Expected:* Refresh token blacklisted; access token cleared; redirect to `/login`. iOS Keychain entry cleared.

---

## 2. Workspaces & Multi-tenancy

### TC-5 Owner invites a teammate
*Persona:* P-1 · *Covers:* FR-1, FR-24 · *Surface:* web
*Pre-conditions:* Owner of a workspace; teammate has email but no account.
*Steps:*
1. Settings → Team → "Invite teammate".
2. Enter teammate email; choose role "Rep".
3. Submit.
4. Teammate receives Resend magic-link email.
5. Teammate clicks link → signup flow auto-pre-fills workspace.
*Expected:* Teammate lands in the workspace as `rep`. Activity log shows "Teammate joined".
*Edge:* `[degraded]` Teammate already exists in another workspace → invite still works; teammate can switch.

### TC-6 Admin promotes a rep to manager
*Persona:* P-3 · *Covers:* FR-1 · *Surface:* web
*Steps:*
1. Settings → Team.
2. Click rep's row; change role dropdown to "Manager".
3. Confirm.
*Expected:* Role updates immediately; rep sees expanded UI on next page load.

### TC-7 User switches workspaces with keyboard
*Persona:* P-2 · *Covers:* FR-1, NFR-2 · *Surface:* web
*Pre-conditions:* User has membership in two workspaces.
*Steps:*
1. Press `Cmd+K`.
2. Type "switch".
3. Select "Switch workspace → Acme Sales".
*Expected:* Workspace context switches; URL updates; data view filters to the new workspace.

### TC-8 Cross-workspace data is invisible
*Persona:* P-2 · *Covers:* FR-1, NFR-3 · *Surface:* API
*Steps:*
1. Authenticate as user-A active in workspace-A.
2. Hit `GET /api/contacts/{contact_id_from_workspace_B}`.
*Expected:* HTTP 403 (or 404 to avoid enumeration). No payload leakage.
*Edge:* `[blocking]` Any leak is a critical security defect.

### TC-9 Owner archives a workspace (soft-delete)
*Persona:* P-1 · *Covers:* FR-1, NFR-8 · *Surface:* web
*Steps:*
1. Settings → Workspace → "Archive workspace" → confirm with workspace name.
*Expected:* Workspace marked deleted; users see archive notice; data retained 30 days.

---

## 3. Contacts & Companies

### TC-10 Rep creates a contact manually
*Persona:* P-2 · *Covers:* FR-3 · *Surface:* web
*Steps:*
1. Press `n` (new) on Contacts list, or click "+ New Contact".
2. Fill first/last name, primary email, phone, title.
3. Optionally link to a company.
4. Save.
*Expected:* Contact appears in list ≤100ms after save; activity row "created" written.
*Edge:* `[degraded]` Duplicate email → toast "Contact already exists" + link to existing.

### TC-11 Rep edits a contact field inline
*Persona:* P-2 · *Covers:* FR-3 · *Surface:* web
*Steps:*
1. Open contact detail.
2. Click title; edit; press Enter.
*Expected:* Save indicator → success in ≤300ms; activity row "title changed" with diff.

### TC-12 Rep archives a contact
*Persona:* P-2 · *Covers:* FR-3 · *Surface:* web
*Steps:*
1. Open contact detail → kebab → Archive.
*Expected:* Contact disappears from default list; visible under "Archived" filter; recoverable for 90 days.

### TC-13 Rep navigates from company → contacts → deals
*Persona:* P-2 · *Covers:* FR-4 · *Surface:* web
*Steps:*
1. Open company detail.
2. Click "Contacts (12)" tab; pick one.
3. From contact, click "Deals (3)" → pick one.
*Expected:* Smooth navigation; back button returns to company.

### TC-14 Bulk-edit company industries
*Persona:* P-3 · *Covers:* FR-4, FR-8 · *Surface:* web
*Steps:*
1. Companies list → multi-select 50 rows.
2. Bulk action → set Industry = "B2B SaaS".
*Expected:* Operation runs as a workflow with progress; activity rows for each company.

---

## 4. Deals & Pipelines

### TC-15 Manager creates a pipeline with custom stages
*Persona:* P-1 · *Covers:* FR-5 · *Surface:* web
*Steps:*
1. Settings → Pipelines → "+ New".
2. Name "Outbound Q3"; add stages "Prospect → Discovery → Demo → Negotiation → Closed Won → Closed Lost".
3. Save.
*Expected:* Pipeline appears in deals view; stages are drag-reorderable.

### TC-16 Rep creates a deal with contact + company
*Persona:* P-2 · *Covers:* FR-5 · *Surface:* web
*Steps:*
1. From a contact's "Deals" tab, click "+ New Deal".
2. Title "Acme Q3 expansion"; value "$24,000"; pipeline "Outbound Q3"; stage "Discovery".
3. Save.
*Expected:* Deal appears in kanban under Discovery; activity logged.

### TC-17 Rep drags a deal across stages
*Persona:* P-2 · *Covers:* FR-5, FR-11 · *Surface:* web
*Steps:*
1. Pipeline kanban view.
2. Drag deal "Acme Q3 expansion" from "Discovery" → "Demo".
*Expected:* Deal moves; activity "stage changed Discovery → Demo"; if a "stage = Demo" automation exists, run starts (TC-29).

### TC-18 Rep closes a deal
*Persona:* P-2 · *Covers:* FR-5 · *Surface:* web
*Steps:*
1. Move deal to "Closed Won".
*Expected:* Deal updates; "Won" badge in tan-text; activity row.

---

## 5. Tasks & Notes

### TC-19 Rep adds a task on a contact
*Persona:* P-2 · *Covers:* FR-6 · *Surface:* web
*Steps:*
1. Contact detail → "Tasks" → "+ New".
2. Title "Send pricing"; due tomorrow 5pm; owner self.
*Expected:* Task appears in "Today" smart view tomorrow; in contact's tasks list now.

### TC-20 Overdue task is highlighted
*Persona:* P-2 · *Covers:* FR-6, NFR-2 · *Surface:* web
*Pre-conditions:* Task whose due is in the past.
*Expected:* Row uses tan-text accent + clear text label "Overdue" (color is not the sole signal).

### TC-21 Rep adds a Markdown note
*Persona:* P-2 · *Covers:* FR-7 · *Surface:* web
*Steps:*
1. Contact detail → Notes tab → "+ New".
2. Body "**Key**: discount-blocked by procurement. Follow up Friday.".
3. Save.
*Expected:* Note rendered with bold; activity row.
*Edge:* `[degraded]` Edit beyond 24h triggers audit-trail row.

---

## 6. Custom fields

### TC-22 Admin adds a custom field "Lead Score"
*Persona:* P-3 · *Covers:* FR-8 · *Surface:* web
*Steps:*
1. Settings → Custom fields → Contacts → "+ New".
2. Type `number`; key `lead_score`; label "Lead Score".
3. Save.
*Expected:* Field appears on contact detail; column toggleable in list view; usable in filter DSL.

### TC-23 Rep filters contacts by custom field
*Persona:* P-2 · *Covers:* FR-8, FR-19 · *Surface:* web
*Steps:*
1. Contacts list → filter → `lead_score > 70`.
*Expected:* Filter applies ≤200ms; result list updates with count.

### TC-24 Admin adds a `select` custom field with options
*Persona:* P-3 · *Covers:* FR-8 · *Surface:* web
*Steps:* Add field type `select`; options "A, B, C".
*Expected:* Drop-down on contact detail; required-flag respected on create.

---

## 7. Email & calendar

### TC-25 Rep connects Gmail
*Persona:* P-2 · *Covers:* FR-9 · *Surface:* web
*Steps:*
1. Settings → Integrations → Gmail → Connect.
2. Complete Google OAuth (read + send + push scopes).
3. Wait for initial sync banner.
*Expected:* Banner reports "Synced last 90 days, 1,243 messages, 312 threads, 87 contacts touched". Each touched contact has email thread visible.

### TC-26 Rep sends an email from a contact view
*Persona:* P-2 · *Covers:* FR-9, FR-13 · *Surface:* web
*Pre-conditions:* Gmail connected.
*Steps:*
1. Contact detail → "Send email".
2. AI suggests a draft based on last 3 messages + deal stage.
3. Edit draft; click Send.
*Expected:* Email sends as the connected user; thread updates in Gmail; activity row "email sent".

### TC-27 Inbound email from a contact creates an activity row
*Persona:* P-2 · *Covers:* FR-9, FR-11 · *Surface:* email + web
*Pre-conditions:* Gmail Pub/Sub push working.
*Steps:* External party replies to the connected user.
*Expected:* Within 30s, contact's activity feed shows "email received". If a workflow has an `email_received` trigger, run starts.

### TC-28 Rep connects Google Calendar and sees meetings on a deal
*Persona:* P-2 · *Covers:* FR-10 · *Surface:* web
*Steps:* Connect GCal; open a deal that has an upcoming meeting.
*Expected:* Meeting appears under "Upcoming" on the deal.

---

## 8. Workflow authoring

### TC-29 Admin builds a 4-step workflow
*Persona:* P-3 · *Covers:* FR-11, FR-12 · *Surface:* web
*Steps:*
1. Automations → "+ New".
2. Trigger: `Deal stage changed to Negotiation`.
3. Drag node: `Wait 1 day`.
4. Drag node: `AI: Draft follow-up email` (model: Sonnet; prompt: comms.draft_reply.v1).
5. Drag node: `Human-in-the-loop approval` → on approve → `Send email`.
6. Connect edges; Save as draft.
7. Click "Publish".
*Expected:* Workflow appears in the active list (version 1). Schema validation passes.

### TC-30 Admin uses "Describe in English" to generate a graph
*Persona:* P-3 · *Covers:* FR-12 · *Surface:* web
*Steps:*
1. New automation → "Describe in English".
2. Type "When a deal goes quiet 5 days, draft a re-engage email and ask me to approve".
3. Click Generate.
*Expected:* Canvas hydrates with: trigger (delay since last activity = 5d) → AI draft → HITL approval → send. User can edit before publishing.

### TC-31 Admin saves a draft and reverts to a prior version
*Persona:* P-3 · *Covers:* FR-12 · *Surface:* web
*Steps:* Edit a published workflow; save as draft; later, restore version 1 from version history.
*Expected:* Active version flips; runs already in flight finish on their original version (per FR-11).

### TC-32 Schema validation blocks publishing a malformed graph
*Persona:* P-3 · *Covers:* FR-12 · *Surface:* web
*Pre-conditions:* Workflow with disconnected node.
*Steps:* Click Publish.
*Expected:* Inline error "Disconnected node 'AI Draft' has no inbound edge"; node highlighted; publish blocked.

---

## 9. Workflow execution & HITL

### TC-33 Workflow run advances correctly through delays
*Persona:* P-1 · *Covers:* FR-11, NFR-7 · *Surface:* admin / web
*Steps:*
1. Trigger TC-29 by moving a deal to Negotiation.
2. Open run inspector; see status `awaiting_delay` with `resume_at` ~24h ahead.
3. Wait (or in dev: clock-skew the resume_at to now-1s).
*Expected:* Run advances to AI Draft step; result captured; status flips to `awaiting_approval`.

### TC-34 Worker restart mid-run loses no state
*Persona:* engineering / P-1 · *Covers:* FR-11, NFR-7 · *Surface:* admin
*Pre-conditions:* Run in `running` after delay; AI step in flight.
*Steps:*
1. Force-kill Celery worker mid-step.
2. Worker restarts.
*Expected:* Idempotency-key short-circuit prevents duplicate AI call; step output recovered; run continues.

### TC-35 Manager approves a HITL step from in-app inbox
*Persona:* P-1 · *Covers:* FR-17, FR-24 · *Surface:* web
*Pre-conditions:* Run in `awaiting_approval` from TC-33.
*Steps:*
1. Open Agent inbox.
2. See approval request with summary + full draft.
3. Click "Approve".
*Expected:* Run resumes; email sends; activity row records decider + decided_at.

### TC-36 Manager approves a HITL step via email magic-link
*Persona:* P-1 · *Covers:* FR-17 · *Surface:* email + web
*Pre-conditions:* Run in `awaiting_approval`.
*Steps:* Click magic link in email; land on signed-token approval page; click Approve.
*Expected:* Run resumes. Token is single-use; second click shows "Already decided".
*Edge:* `[blocking]` Token expired (>7d) → "Decision window closed" message; run remains paused.

### TC-37 Manager approves a HITL step via iOS push
*Persona:* P-1 · *Covers:* FR-17, FR-23 · *Surface:* iOS push + iOS app
*Pre-conditions:* iOS app installed + push enabled; run in `awaiting_approval`.
*Steps:* Receive push; long-press → Approve action.
*Expected:* Approval registered without unlocking the app; activity row records "approved via iOS push".

### TC-38 Reversible autonomous action is undoable for 60s
*Persona:* P-2 · *Covers:* FR-17 · *Surface:* web
*Pre-conditions:* Workspace policy `add_internal_note` = `autonomous`.
*Steps:*
1. Agent autonomously adds a note.
2. Within 60s, click "Undo" toast.
*Expected:* Note removed; activity row records autonomous-action + undo.

### TC-39 Workflow retries on transient failure
*Persona:* P-3 · *Covers:* FR-11, NFR-7 · *Surface:* admin
*Pre-conditions:* HTTP step pointing at an endpoint that flaps.
*Steps:* Trigger workflow; first request fails with 503; wait.
*Expected:* Step retries with exponential backoff (3 attempts); final attempt logged either success or hard-fail with detail.

---

## 10. AI: comms intelligence

### TC-40 AI drafts a reply with streaming
*Persona:* P-2 · *Covers:* FR-13, NFR-1 · *Surface:* web
*Steps:* Contact view → "AI draft reply"; first token visible ≤1.5s P95.
*Expected:* Streaming appears chunk-by-chunk; final draft editable.

### TC-41 Thread summary appears on Gmail thread open
*Persona:* P-2 · *Covers:* FR-13 · *Surface:* web
*Pre-conditions:* Gmail thread with ≥6 messages.
*Steps:* Open thread.
*Expected:* 3-bullet summary at top within 2s; cached for the thread's `last_message_at`.

### TC-42 Meeting summary writes to deal activity
*Persona:* P-2 · *Covers:* FR-13, FR-10 · *Surface:* web
*Steps:* On a deal, paste a meeting transcript → "Summarize".
*Expected:* 5-bullet summary written to the deal's activity log; cost displayed in admin telemetry.

---

## 11. AI: NL data layer

### TC-43 Manager runs a natural-language query in cmd-K
*Persona:* P-1 · *Covers:* FR-14, FR-19, NFR-1 · *Surface:* web
*Steps:*
1. `Cmd+K`.
2. Type "deals over $10k that went quiet last week".
3. Press Enter.
*Expected:* Filtered list ≤2s P95; "Save as view" affordance; AI summary above ("12 deals, 60% in Negotiation, average value $18k").

### TC-44 NL query handles fuzzy phrasing via vector rerank
*Persona:* P-1 · *Covers:* FR-14, FR-19 · *Surface:* web
*Steps:* Type "deals that smelled risky".
*Expected:* Hybrid keyword + vector results; AI summary explains why each is flagged.

### TC-45 Saved view persists per workspace
*Persona:* P-2 · *Covers:* FR-14 · *Surface:* web
*Steps:* Save TC-43's view as "Quiet >$10k"; visible to teammates with appropriate role.

---

## 12. AI: lead scoring & enrichment

### TC-46 New contact triggers enrichment
*Persona:* P-2 · *Covers:* FR-15 · *Surface:* web
*Steps:* Add contact `john@stripe.com`.
*Expected:* Within 60s, contact's company shows industry "Payments", size "1000+"; lead score populated as a number.

### TC-47 Per-workspace token budget halts enrichment
*Persona:* P-3 · *Covers:* FR-15, NFR-6 · *Surface:* admin
*Pre-conditions:* Daily budget set very low.
*Steps:* Add many contacts in a row.
*Expected:* After budget hit, enrichment workers pause; admin gets in-app + email notice; queued work resumes next budget window.

### TC-48 Manual re-score recomputes a lead
*Persona:* P-2 · *Covers:* FR-15 · *Surface:* web
*Steps:* Contact detail → "Re-score" button.
*Expected:* Score recomputed within 5s; previous score recorded in activity diff.

---

## 13. AI: suggested next actions

### TC-49 Quiet deal shows a suggestion
*Persona:* P-2 · *Covers:* FR-16 · *Surface:* web
*Pre-conditions:* Deal stage stable >5 days.
*Steps:* Open deal.
*Expected:* Suggestion strip shows "This deal hasn't moved in 5 days — draft a re-engage email?".
*Edge:* Dismissed suggestion does not reappear for 7 days.

### TC-50 Suggestion converts to a workflow
*Persona:* P-3 · *Covers:* FR-12, FR-16 · *Surface:* web
*Steps:* Suggestion → "Make this a workflow".
*Expected:* Canvas opens with a draft graph implementing the suggestion's intent.

---

## 14. AI: agent autonomy + HITL

### TC-51 Admin sets workspace policy table
*Persona:* P-3 · *Covers:* FR-17 · *Surface:* web
*Steps:* Settings → Agent → set `send_email_to_contact` = approve, `post_slack` = autonomous, `update_note` = autonomous.
*Expected:* Policy persists; visible in agent inbox legend.

### TC-52 Rep enables Agent assist on a deal
*Persona:* P-2 · *Covers:* FR-17 · *Surface:* web
*Steps:* Deal detail → "Agent assist" toggle.
*Expected:* Agent runs a planning loop; proposes ≤N actions; per-action mode comes from the policy table.

### TC-53 Mixed approve/autonomous batch flows correctly
*Persona:* P-1 · *Covers:* FR-17 · *Surface:* web + iOS
*Pre-conditions:* TC-52 active; agent proposes (1) Slack note (autonomous), (2) email to contact (approve), (3) calendar invite (approve).
*Expected:* Slack action runs immediately with undo affordance; emails and invites pause as `awaiting_approval`; user can approve from web inbox or iOS push.

### TC-54 Audit log captures every agent action
*Persona:* P-3 · *Covers:* FR-17, FR-25 · *Surface:* admin
*Steps:* Audit log filter `actor_kind = agent`.
*Expected:* Each row shows prompt name, model, cost, output, decision, decider.

---

## 15. Search

### TC-55 Cmd-K opens fast and ranks correctly
*Persona:* P-2 · *Covers:* FR-19, NFR-1 · *Surface:* web
*Steps:* Press `Cmd+K`; type "ac" (3 chars).
*Expected:* Open ≤80ms; first results ≤200ms; Acme Corp + Acme Ltd ranked above Carmackdyne.

### TC-56 Recent searches surface
*Persona:* P-2 · *Covers:* FR-19 · *Surface:* web
*Steps:* Open cmd-K with empty input.
*Expected:* Last 5 queries listed.

### TC-57 Search across notes and emails
*Persona:* P-2 · *Covers:* FR-19 · *Surface:* web
*Steps:* Search "procurement blocking".
*Expected:* Hits in notes + emails; filters by entity type chips.

---

## 16. Import (CSV, HubSpot, Pipedrive)

### TC-58 Admin imports a 5k-row CSV
*Persona:* P-3 · *Covers:* FR-20, FR-11 · *Surface:* web
*Steps:*
1. Settings → Import → CSV.
2. Drop file; AI suggests column → field mapping; user reviews.
3. Click Import.
*Expected:* Import runs as a workflow; progress visible; final report shows successes + skipped (with reasons).

### TC-59 HubSpot import handles deals + contacts + companies
*Persona:* P-3 · *Covers:* FR-20 · *Surface:* web
*Steps:* Paste HubSpot export URL; pick objects; map; import.
*Expected:* Cross-references preserved (deal → contact → company); custom HubSpot fields land in custom fields where types align.

### TC-60 Pipedrive import handles pipeline stages
*Persona:* P-3 · *Covers:* FR-20, FR-5 · *Surface:* web
*Expected:* Pipeline stages from Pipedrive create matching pipeline; deals land in correct stages.

### TC-61 Import resumes after worker restart
*Persona:* P-3 · *Covers:* FR-20, NFR-7 · *Surface:* admin
*Steps:* Kill worker mid-import.
*Expected:* On restart, idempotency keys prevent re-creating already-imported rows; remaining rows continue.

---

## 17. Slack & webhooks

### TC-62 Admin connects Slack
*Persona:* P-3 · *Covers:* FR-21 · *Surface:* web
*Steps:* Settings → Integrations → Slack → OAuth.
*Expected:* Channels list visible; can be picked in workflow Slack nodes.

### TC-63 Workflow posts to Slack
*Persona:* P-3 · *Covers:* FR-11, FR-21 · *Surface:* web → Slack
*Pre-conditions:* TC-62 done; workflow with Slack node.
*Steps:* Trigger workflow.
*Expected:* Message appears in target channel ≤5s; activity row logs.

### TC-64 Inbound webhook fires a workflow
*Persona:* P-3 · *Covers:* FR-22, FR-11 · *Surface:* HTTP → web
*Steps:* Copy webhook URL from a workflow's webhook trigger; POST a JSON payload from `curl` with HMAC header.
*Expected:* Workflow run starts ≤2s; payload visible in run inspector.

### TC-65 Outbound HTTP step with bearer auth
*Persona:* P-3 · *Covers:* FR-22 · *Surface:* web → HTTP
*Steps:* Workflow with HTTP node calling external API with bearer token preset.
*Expected:* Request body + headers correct; response captured in step output.

---

## 18. Notifications

### TC-66 User disables email for `task_due_soon`
*Persona:* P-2 · *Covers:* FR-24 · *Surface:* web
*Steps:* Settings → Notifications → uncheck email for task_due_soon.
*Expected:* In-app + push still on; email skipped.

### TC-67 Quiet hours suppress non-HITL pushes
*Persona:* P-2 · *Covers:* FR-24 · *Surface:* iOS
*Pre-conditions:* Quiet hours 9pm–7am set.
*Steps:* Trigger a non-HITL push at 11pm.
*Expected:* Push deferred to 7am; HITL approval push during same window arrives immediately.

---

## 19. iOS app

### TC-68 iOS launches to "today" view fast
*Persona:* P-2 · *Covers:* FR-23, NFR-1 · *Surface:* iOS
*Pre-conditions:* Logged in.
*Steps:* Cold-start the app.
*Expected:* "Today" view rendered ≤2s P95 on a 3-year-old iPhone.

### TC-69 iOS edits a deal offline and syncs on reconnect
*Persona:* P-2 · *Covers:* FR-23, NFR-7 · *Surface:* iOS
*Steps:*
1. Toggle airplane mode.
2. Edit deal value; save.
3. Re-enable network.
*Expected:* Edit queued + flagged "pending sync"; on reconnect, sync runs; activity row logs the edit time.

### TC-70 iOS HITL approval bypasses lock screen
*Persona:* P-1 · *Covers:* FR-17, FR-23, FR-24 · *Surface:* iOS push
*Steps:* Receive HITL push on lock screen; long-press → Approve.
*Expected:* Approval succeeds without app unlock.

### TC-71 iOS pull-to-refresh reloads list
*Persona:* P-2 · *Covers:* FR-23 · *Surface:* iOS
*Expected:* Last-updated timestamp + spinner; new records appear if any.

---

## 20. Reports & dashboards

### TC-72 Workspace home shows pipeline + activity
*Persona:* P-1 · *Covers:* FR-18, NFR-1 · *Surface:* web
*Steps:* Land on workspace home.
*Expected:* Cached aggregates load ≤500ms P95; deal funnel chart rendered; activity-over-time chart rendered.

### TC-73 Drill from counter into underlying records
*Persona:* P-4 · *Covers:* FR-18 · *Surface:* web
*Steps:* Click counter "Deals in Negotiation: 12".
*Expected:* Filtered list of those 12 deals.

### TC-74 Charts respect color-not-sole-signal a11y
*Persona:* P-4 · *Covers:* FR-18, NFR-2 · *Surface:* web
*Expected:* Status badges include text labels in addition to color.

---

## 21. Accessibility

### TC-75 Keyboard-only walk through every flow
*Persona:* any · *Covers:* NFR-2 · *Surface:* web
*Steps:* Disable mouse; navigate signup → workspace → contacts → deal → workflow author.
*Expected:* Every interactive element reachable via Tab/Shift-Tab; cmd-K + j/k + slash work; focus-visible ring (tan, 2px, 2px offset) on every focused element.

### TC-76 Reduced motion collapses animations
*Persona:* any · *Covers:* NFR-2 · *Surface:* web + iOS
*Pre-conditions:* OS reduced-motion enabled.
*Expected:* Page transitions, skeleton shimmer, agent suggestion fade-in collapse to instant.

### TC-77 Skip link focuses on Tab from page top
*Persona:* any · *Covers:* NFR-2 · *Surface:* web
*Steps:* Load page; press Tab.
*Expected:* "Skip to content" link appears; activating it focuses main.

### TC-78 Axe-clean on top-level routes
*Persona:* engineering · *Covers:* NFR-2 · *Surface:* web
*Steps:* Run axe-core against /, /contacts, /deals, /automations/<id>/edit, /brand.
*Expected:* No violations of severity ≥serious.

### TC-79 Screen reader pass on a deal flow
*Persona:* any · *Covers:* NFR-2 · *Surface:* web
*Pre-conditions:* VoiceOver or NVDA running.
*Expected:* Deal name, stage, value, owner all announced; kanban drag has keyboard-equivalent (move-to dropdown).

---

## 22. Performance

### TC-80 Page-to-page nav P95 budget
*Persona:* engineering · *Covers:* NFR-1 · *Surface:* web
*Steps:* RUM measurement on contacts → deal → company → contacts navigations.
*Expected:* P95 ≤300ms.

### TC-81 1k-contact list paginates smoothly
*Persona:* P-2 · *Covers:* NFR-1 · *Surface:* web
*Steps:* Scroll, filter change.
*Expected:* No frame drops below 50fps; filter change ≤200ms.

### TC-82 100-node workflow canvas does not jank
*Persona:* P-3 · *Covers:* FR-12, NFR-1 · *Surface:* web
*Steps:* Open a 100-node workflow; pan, zoom, drag.
*Expected:* Canvas responsive ≥45fps.

### TC-83 Workflow advancer step latency budget
*Persona:* engineering · *Covers:* FR-11, NFR-1 · *Surface:* admin
*Steps:* Run a 10-step workflow without delays/AI.
*Expected:* Per-step advancer latency P95 ≤500ms.

---

## 23. Error & empty states

### TC-84 Empty contacts list invites import
*Persona:* P-2 · *Covers:* FR-3, FR-20 · *Surface:* web
*Pre-conditions:* New workspace with 0 contacts.
*Expected:* Empty state shows "No contacts yet — import from CSV / HubSpot / Pipedrive, or create one." with CTAs.

### TC-85 Workflow build error is recoverable
*Persona:* P-3 · *Covers:* FR-12 · *Surface:* web
*Pre-conditions:* Workflow with invalid node config.
*Steps:* Click Save / Publish.
*Expected:* Inline error highlights bad node; canvas state preserved; user can fix.

### TC-86 AI provider outage falls back gracefully
*Persona:* P-2 · *Covers:* FR-13, NFR-6 · *Surface:* web
*Pre-conditions:* Anthropic returns 503.
*Steps:* Request a draft.
*Expected:* Router falls back to OpenAI; degraded notice in admin telemetry; user sees a draft (possibly with "fallback model" label).

### TC-87 Loading state shows skeleton not blank
*Persona:* any · *Covers:* NFR-1 · *Surface:* web + iOS
*Expected:* Each route ships an idiomatic skeleton; never a blank flash.

### TC-88 Network failure on iOS shows cached data + retry
*Persona:* P-2 · *Covers:* FR-23 · *Surface:* iOS
*Pre-conditions:* Offline.
*Expected:* Last-cached data visible with "Offline" badge; retry button.

---

## 24. Audit & privacy

### TC-89 Admin views a 30-day audit slice
*Persona:* P-3 · *Covers:* FR-25 · *Surface:* web
*Steps:* Audit log filter `last 30 days, kind = field_changed, entity = deal`.
*Expected:* Table of changes with actor + diff; CSV export available.

### TC-90 Right-to-delete cascades within 30 days
*Persona:* P-1 · *Covers:* NFR-8 · *Surface:* web + admin
*Steps:* Owner requests workspace deletion.
*Expected:* Workspace soft-deleted; 30-day countdown banner; after 30 days a job hard-deletes all workspace data including S3/Spaces objects and embedding rows.

### TC-91 AI prompts never leak across workspaces
*Persona:* engineering · *Covers:* NFR-3, NFR-8 · *Surface:* admin
*Steps:* In a test, force two simultaneous AI calls from different workspaces with overlapping content.
*Expected:* Prompt cache keys are workspace-scoped; one workspace's data never appears in another workspace's response context.

---

## Appendix A — Surface-coverage matrix (MVP P0)

| Functional area | Web | iOS | API | Workflow |
|---|---|---|---|---|
| Auth & workspaces | ✓ | ✓ | ✓ | — |
| Contacts/Companies/Deals/Tasks | ✓ | ✓ | ✓ | ✓ (mutate) |
| Custom fields | ✓ | (read) | ✓ | ✓ (mutate) |
| Email/Calendar sync | ✓ | (read activity) | ✓ | ✓ (trigger + send) |
| Workflow authoring | ✓ | — | ✓ | — |
| Workflow execution | (run inspector) | (HITL) | ✓ | ✓ |
| AI: comms / NL / next-actions / scoring | ✓ | (next-actions read) | ✓ | ✓ |
| Agent autonomy + HITL | ✓ | ✓ (push + approve) | ✓ | ✓ |
| Reports | ✓ | (light) | ✓ | — |
| Search | ✓ | ✓ | ✓ | — |
| Import | ✓ | — | ✓ | ✓ |
| Slack | ✓ (configure) | — | ✓ | ✓ (action) |
| Webhooks / HTTP | ✓ (configure) | — | ✓ | ✓ |
| Audit | ✓ | — | ✓ | — |

---

## Appendix B — Test execution lanes

- **Smoke** (≤10 min) — TC-1, TC-7, TC-10, TC-15, TC-25, TC-29, TC-43, TC-55, TC-68. Run before every deploy.
- **Pre-release** — every test case TC-1..TC-91. Run before each milestone-ending demo.
- **Continuous** (Playwright web) — auth, workspace switch, contact/deal CRUD, cmd-K, brand a11y. Runs on every PR.
- **iOS regression** (XCUITest) — login, list, detail, HITL push approve. Runs on every iOS build.

---

*TESTING.md ends.*
