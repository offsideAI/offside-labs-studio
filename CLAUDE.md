# CLAUDE.md

> Instructions for Claude Code (and humans new to the repo) working in the Offside Studio Suite monorepo. **Read this first.**

This is the Offside Studio Suite monorepo. **Offside CRM** is product #1 of 4 (Crunch / Design / Director follow). Stay grounded in the source-of-truth docs before acting.

## Read these in order

1. **[PLAN.md](./PLAN.md)** — architecture, stack, monorepo layout, automation engine, brand system, 16 milestones (M0–M15) and 15 post-MVP placeholder phases.
2. **[PRD.md](./PRD.md)** — product requirements with stable IDs (`FR-1` … `FR-25`, `NFR-1` … `NFR-8`, `POST-1` … `POST-15`). Every FR/NFR/POST carries a `[✅]/[🏗️]/[☑️]` status checkbox.
3. **[TESTING.md](./TESTING.md)** — 91 user-perspective E2E test cases (`TC-1` … `TC-91`) across 24 functional areas.
4. **[ROADMAP.md](./ROADMAP.md)** — phases mapped 1:1 to epics, with user stories + engineering tasks + acceptance criteria + estimates. Every milestone/story/task carries the same `[✅]/[🏗️]/[☑️]` status checkbox.
5. **[MEMORY.md](./MEMORY.md)** — running record of state, locked decisions, and watch-outs. Living document.

## Current milestone progress

- **Shipped on `main`:** M0 (scaffold) · M1 (auth) · M2 (workspaces) · M3 (cmd-K shell) · M4 (records + CSV import) · M5 (deals + tasks + notes + activities) · M6 (iOS read-only shell) · M7 (durable workflow runtime).
- **Next up:** **M8 — workflow node-graph editor (React Flow)** with describe-in-English Claude prompt. Maps to TC-29..TC-32.
- **Status checkbox legend (PRD.md + ROADMAP.md):** `[✅]` implemented · `[🏗️]` partially implemented · `[☑️]` pending. Keep PRD and ROADMAP checkboxes synced when you complete or partially deliver a piece of work.

## Stack at a glance

| Surface | Choice | Where |
|---|---|---|
| Web frontend | Next.js 15 + TypeScript strict (Vercel) | `frontend-web/` |
| Backend + workflow runtime | Django 4.2 + DRF + Celery 5 + Redis (Digital Ocean App Platform) | `backend/` |
| iOS | SwiftUI 17+, xcodegen-generated project | `frontend-ios/` |
| Suite placeholders | Next.js 10-line shells | `crunch-web/`, `design-web/`, `director-web/` |
| Shared TS code | pnpm workspaces + Turborepo | `packages/{ui,ai,auth-utils,workflows-sdk,api-client,config}` |
| Database | Postgres 16 + pgvector (HNSW) | DO Managed Postgres |
| Auth | django-allauth + dj-rest-auth + djangorestframework-simplejwt; custom email-based User | backend |
| API contract | OpenAPI 3.1 from drf-spectacular → openapi-typescript (web) + Swift codegen (iOS) | `tools/openapi/` |
| AI | Anthropic Claude default + OpenAI/Gemini fallback | `packages/ai` (TS) + `backend/apps/ai` (Py) |
| Transactional email | Resend | backend |
| Domains | `app.offside.ai` (web), `crm-api.offside.ai` (Django), `platform.offside.ai` (marketing) | DNS |

## Brand discipline (load-bearing — non-negotiable)

The OffsideAI Design System v1.0 is authoritative. Tokens live in `packages/ui/src/styles/tokens.css` (adopted verbatim from the offside.ai marketing site CSS).

- **Tan `#C9A389`** is the only saturated brand color. **Emphasis only — never a fill.**
- **Light-first.** Bone `#F1F1F1` is the primary surface. Dark `#161616` is scoped per section (code panels, hero, footer) — never a global toggle.
- **`--brand-tan-text` is `#7A5F44`** — the WCAG-safe tan-on-bone token. Brand book listed `#B8916F`; that fails contrast (2.54:1 on Bone). **Do not "correct" back to the brand-book hex.**
- **Display:** Styrene A (paid, Commercial Type) → Söhne → Inter → system. **Body:** Roboto. **Mono:** JetBrains Mono. **Icons:** Lucide 1.5–2px stroke.
- **Voice:** engineer-to-engineer. Sentence-case headers ending with a period. UPPERCASE eyebrows tracked 0.18em. Sentence-case CTAs — never ALL CAPS. Never breathless.

### Forbidden in any UI surface
- Saturated blue, purple, magenta, cyan — explicitly off-brand.
- Dark-mode-as-global default — only scoped dark sections.
- Any font outside the locked stack.
- Marketing copy with "revolutionary," "game-changing," "supercharged," "unleash," and similar adjective inflation.

## Workflow engine

We do **not** use Inngest. The runtime is **Celery + Redis + a custom Django durable layer** at `backend/apps/automations` (see PLAN.md §7). Inngest was originally proposed and explicitly rejected by the user (DO App Platform constraint). Don't reintroduce it.

The custom layer owns:
- `Automation` / `AutomationRun` / `AutomationStepRun` / `HitlRequest` / `AgentPolicy` Django models.
- A `run_advancer(run_id)` Celery task that walks the workflow graph durably.
- Idempotency keyed by `(run_id, step_id, attempt)`.
- HITL pause via `automation_run.status = awaiting_approval` + signed approval token.
- A "wake-up sweep" Beat task that re-enqueues advancers for delayed/waiting runs.

Hatchet is on the shelf as a fallback if the custom layer's complexity grows past M9.

## Common commands

```bash
pnpm install                    # JS deps across the workspace
pnpm dev                        # all 4 web apps in parallel (3000/3001/3002/3003)
pnpm backend:up                 # Postgres + Redis + Django web + Celery worker + Celery Beat (docker compose)
pnpm backend:down               # tear down the local backend
pnpm codegen:openapi            # regenerates @offside/api-client + frontend-ios/Generated from Django's OpenAPI
pnpm ios:gen                    # xcodegen → frontend-ios/OffsideCRM.xcodeproj
pnpm typecheck                  # TS across all packages
pnpm lint                       # lint across all packages
pnpm format                     # prettier write
```

## Conventions

- **Type-safe end-to-end.** No `any` in TS. OpenAPI codegen runs on every PR; CI fails on schema drift.
- **Every AI call surfaces UX affordance + telemetry.** No silent LLM bills. Every call logs `{prompt_name, model, tokens_in, tokens_out, cost_cents, latency_ms, run_id?, step_id?}`.
- **Workflow side effects are idempotency-keyed** by `(run_id, step_id, attempt)`. Action handlers short-circuit on cached output.
- **Workspace-scoped data isolation** enforced at the Django ORM layer via `WorkspaceScopedMixin` + DRF permission class. Cross-workspace leakage is a critical security defect.
- **A11y from day one** — keyboard nav (Cmd-K, j/k, /, esc), focus-visible 2px tan ring with 2px offset, skip-link, axe-clean smoke pass on every route.
- **Stable IDs in docs** — never reuse a retired `FR-N` / `NFR-N` / `POST-N` / `TC-N` / `M-N` / `POST-N`. Append; don't recycle.
- **No mock data in production paths.** Seed scripts under `tools/seeds/` are fine; hard-coded fake data in components is not.
- **Don't auto-create docs.** Do not add `.md` files unless the user explicitly requests them.

## Don't

- Don't suggest dark-first UI as the default.
- Don't suggest violet, blue, purple, magenta, or cyan accents.
- Don't reintroduce Inngest.
- Don't refactor the flat monorepo back into `apps/*`.
- Don't copy code from `../radianceskincare-app/saucycart-com-backend-django/`. It is **reference only**.
- Don't add new dependencies without asking the user (per the brief's ground rules).
- Don't push to `origin` without explicit user instruction.
- Don't use `--no-verify` or `--no-gpg-sign` on commits.
- Don't run `git add -A` or `git add .` — always stage by name.

## When the plan changes

If the user pivots a major decision mid-stream (e.g., changes the workflow engine, the monorepo shape, the auth stack), **update PLAN.md first** before continuing implementation. Then propagate to PRD.md / TESTING.md / ROADMAP.md / MEMORY.md as needed. Don't keep building on a stale plan.

## Escalation

When you find a contradiction between the original brief and what the user is now asking for, surface it explicitly with a "was → now → why" diff and ask. The user expects pushback when their answer conflicts with their own prior constraints — past examples include flagging the Django backend pivot vs the brief's web-first stance and the brand book's contrast failure on `#B8916F`.

## Where things are referenced (sibling repos)

These live as siblings of this repo at `/Users/coder/repos/offsideai/githubrepos_workspace_active_1/`:

- **`OffsideLabs-AI/offsidelabs-ai-web/`** — Nuxt marketing site. **Brand source of truth** at `assets/css/tailwind.css`. Favicon (OA monogram, two overlapping tan circles) at `public/favicon.svg`.
- **`radianceskincare-app/saucycart-com-backend-django/`** — SaucyCart B2B services backend. Reference for multi-tenancy patterns + Procfile + DO App Platform shape. **Code is not copied.**

---

*This file is committed to the repo. Update as conventions evolve.*
