# MEMORY.md

> Running record of project state, locked decisions, and watch-outs. Companion to [PLAN.md](./PLAN.md) / [PRD.md](./PRD.md) / [TESTING.md](./TESTING.md) / [ROADMAP.md](./ROADMAP.md) — but **more living**. Update as state changes.

## Current state (2026-05)

- **Branch:** `main`. Local is **9 commits ahead of `origin/main`** — not yet pushed.
- **Latest commits (newest first):**
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
  - **M0 — complete.** Repo skeleton resolves end-to-end: `pnpm install` resolves all workspaces, `pnpm dev` runs all four web apps (3000/3001/3002/3003), `pnpm backend:up` boots Django + Postgres + Redis + Celery worker + Beat via docker-compose, `pnpm ios:gen` generates a buildable Xcode project, GitHub Actions CI runs on push + PR.
  - **M1 — complete.** `apps/users` ships a custom email-based User with hand-authored 0001_initial migration; allauth + dj-rest-auth + SimpleJWT wired in JWT mode at `/api/auth/*`; `/api/schema/` serves OpenAPI publicly so `pnpm codegen:openapi` produces a typed `schema.ts`; Celery `ping` task imports + runs; pytest covers signup → login → /api/auth/user/ + Celery + schema. Production settings tighten JWT cookies to secure + force ACCOUNT_DEFAULT_HTTP_PROTOCOL=https.
  - **M2 — complete.** `apps/workspaces` ships Workspace + Membership + Role + Invitation with role-based permission classes (IsWorkspaceMember/Owner/Admin/Manager) + WorkspaceJWTAuthentication that resolves the active workspace from the X-Workspace-Id header (NOT a JWT claim — workspace switching is zero-token-rotation). Invite flow via Resend magic-link templates is end-to-end with public + authenticated accept endpoints. Frontend ships login + signup + onboarding + accept-invite/[token] + protected `/[workspace]/` route group with a working WorkspaceSwitcher; data layer is TanStack Query v5; `@offside/auth-utils` has a real authFetch with refresh-on-401 + workspace-header injection. **Deferred to later milestones:** TC-6 (role promotion UI — settings page lands in M3+), TC-7 (cmd-K keyboard switch — full palette is M3), TC-9 (workspace archive UI — settings page).
  - **M3 — pending (next).** Web shell + cmd-K palette + j/k row nav + slash search + skip link + axe-clean smoke pass on every route. Lands TC-7, TC-75–TC-79.
  - **M4–M15 — pending.** Per [ROADMAP.md](./ROADMAP.md).

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

M2 is complete. **Next milestone is M3 (web shell + cmd-K palette + keyboard nav).**

Verify M2 locally first:
1. `pnpm install` (picks up @tanstack/react-query). `pnpm backend:up` + `pnpm backend:migrate` + `pnpm backend:test` (the new workspace tests should pass).
2. `pnpm dev` (in another shell) → http://localhost:3000/signup → create account → manually flip `EmailAddress.verified=True` in Django shell or set `ACCOUNT_EMAIL_VERIFICATION=optional` → /login → /onboarding → /{slug}.
3. From the workspace home, invite a teammate; check the worker logs for the Resend send (or set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in dev to print the magic link).

To start M3 from a cold context:
1. **App shell** — `frontend-web/components/AppShell.tsx` with a sidebar (collapsible) + top bar + main slot. Replace the ad-hoc header in `app/[workspace]/layout.tsx` with this shell.
2. **Cmd-K palette skeleton** — install `cmdk` (or build with React); fuzzy-match commands + workspaces. Real record/search hooks land in M12; M3 ships the chassis + workspace switcher + nav-to-page commands.
3. **Keyboard primitives** — `j/k` row nav (a `useListKeyboardNav` hook), `/` to focus search, `n` to create-new, `esc` to close modals/popovers, focus trap on dialogs.
4. **Skip link + a11y** — already present in `app/layout.tsx`; verify it's visible on Tab + axe-clean.
5. **Polish auth pages** — login/signup/onboarding/accept-invite get the new shell-less layout (centered card on bone) consistent with brand.
6. **Tests** — TC-7, TC-55, TC-75, TC-76, TC-77, TC-78, TC-79 (Playwright if we add it; otherwise manual scripts).

Open `§14.1` items still defer-able. The first ones that bite during M3 are: full logo wordmark SVG (currently using OA monogram favicon only), per-product hue confirmation (only matters if Crunch placeholder gets real chrome).

## Revision log

- **2026-05** — initial commit `5375384`. PLAN.md rev 2 (Celery substitute, DO App Platform, flat monorepo). PRD / TESTING / ROADMAP added. M0 phase 1 scaffolded.
- **2026-05** — `0090063` added CLAUDE.md + MEMORY.md (this file) for durable repo-level context.
- **2026-05** — `dd2a003` scaffolded M0 phase 2a: `frontend-web/` (Next.js 15 + `/brand` token-demo route) and the three suite placeholders (`crunch-web`, `design-web`, `director-web`).
- **2026-05** — `d48c5ed` completed M0: Django backend (Celery + Procfile + Dockerfile + docker-compose + `apps.health` for liveness/readiness), `frontend-ios/` (xcodegen + SwiftUI placeholder with brand-token parity), GitHub Actions CI workflow. M0 done.
- **2026-05** — `268922c` updated MEMORY.md to mark M0 complete + add the M1 cold-context pickup guide.
- **2026-05** — `4ed442e` completed M1: `apps/users` (email-based custom User, hand-authored 0001 migration, UserAdmin, serializers), allauth + dj-rest-auth + SimpleJWT wired at `/api/auth/*`, public OpenAPI schema, real `openapi-typescript` codegen, conftest.py forcing Celery eager + locmem email in tests, signup/login/me + Celery + schema-served pytest coverage, prod settings tightening JWT cookies + ACCOUNT_DEFAULT_HTTP_PROTOCOL=https. M1 done.
- **2026-05** — `11b785f` updated MEMORY.md to mark M1 complete + add the M2 cold-context pickup guide.
- **2026-05** — `d9cc5ec` completed M2 backend: `apps/workspaces` with Workspace + Membership + Role + Invitation models, hand-authored 0001 migration, IsWorkspace{Member|Owner|Admin|Manager} permission classes, WorkspaceJWTAuthentication that resolves active workspace via X-Workspace-Id header, invite flow with Resend magic-link template, public + authenticated accept endpoints, comprehensive pytest coverage (workspace creation, invite + accept round-trip, cross-workspace 403, wrong-email 403, invalid-header 403). Settings switched to the workspace-aware auth class.
- **2026-05** — `5ee2c33` completed M2 frontend: `@offside/auth-utils` real implementation (memory + browser TokenStores, authFetch with refresh-on-401 and X-Workspace-Id auto-injection), `frontend-web/lib/api.ts` (TanStack Query v5 hooks for current user, workspaces, memberships, invitations, public + accept invitation), `lib/contexts.tsx` (WorkspaceProvider resolving slug → active workspace, AuthGate for client-side redirects), `app/providers.tsx` (QueryClientProvider + auth-failure handler), pages for /login, /signup, /onboarding, /accept-invite/[token], /[workspace]/{layout,page}, and a WorkspaceSwitcher component. Path-segment routing (`/{workspace-slug}/...`) is the canonical convention. M2 done — TC-6 (role promotion UI), TC-7 (cmd-K keyboard switch), and TC-9 (workspace archive UI) deferred to M3+ as documented in commit body.

---

*Update this file when state changes. Treat the "Current state" section as the authoritative pointer for "where are we right now."*
