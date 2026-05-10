# Offside Studio Suite

Monorepo for the Offside Studio Suite. The CRM is product #1; Crunch / Design / Director follow.

> **Read [PLAN.md](./PLAN.md) first.** It's the source of truth for product scope, architecture, brand, and the build sequence. Everything below is a quick map.

## Layout

```
offside-labs-studio/
├─ frontend-web/        # Next.js 15 App Router (Vercel)            — CRM web
├─ backend/             # Django + DRF + Celery (DO App Platform)   — CRM API + workflow runtime
├─ frontend-ios/        # SwiftUI (xcodegen)                        — CRM iOS
├─ crunch-web/          # Next.js placeholder                       — Suite app #2
├─ design-web/          # Next.js placeholder                       — Suite app #3
├─ director-web/        # Next.js placeholder                       — Suite app #4
├─ packages/
│  ├─ ui/               # @offside/ui — brand tokens + shadcn-keyed components
│  ├─ ai/               # @offside/ai — model router + prompt registry (TS twin of backend/apps/ai)
│  ├─ auth-utils/       # @offside/auth-utils — JWT helpers, fetch interceptors
│  ├─ workflows-sdk/    # @offside/workflows-sdk — typed events + action client
│  ├─ api-client/       # @offside/api-client — generated TS client from OpenAPI
│  └─ config/           # @offside/config — shared TS / Tailwind / ESLint config
├─ tools/
│  ├─ openapi/          # OpenAPI → TS + Swift codegen scripts
│  └─ seeds/            # Demo seed scripts (Django mgmt commands)
├─ PLAN.md
└─ README.md
```

## Prerequisites

- Node ≥ 20, pnpm ≥ 9
- Python ≥ 3.11
- Docker + Docker Compose (for local Postgres + Redis)
- Xcode 16 + xcodegen (for iOS — `brew install xcodegen`)

## Local dev

```bash
# 1. Install JS deps
pnpm install

# 2. Start backend + Postgres + Redis
pnpm backend:up                 # docker compose for postgres + redis + django web + celery worker + beat

# 3. Start all web apps in parallel
pnpm dev                        # frontend-web + crunch-web + design-web + director-web

# 4. (Optional) Generate iOS Xcode project
pnpm ios:gen                    # runs xcodegen inside frontend-ios/
```

The web apps run on:

| App         | Local port |
|-------------|------------|
| frontend-web (CRM) | 3000 |
| crunch-web         | 3001 |
| design-web         | 3002 |
| director-web       | 3003 |

Backend Django runs on `localhost:8000` (admin at `/admin/`, OpenAPI at `/api/schema/`).

## Domains

| Surface           | Production domain          |
|-------------------|----------------------------|
| CRM web           | `app.offside.ai`           |
| CRM API (Django)  | `crm-api.offside.ai`       |
| Marketing site    | `platform.offside.ai`      |

## Brand

Source of truth: [PLAN.md §9](./PLAN.md#9-brand--design-system) + `packages/ui/src/styles/tokens.css` (adopted verbatim from `OffsideLabs-AI/offsidelabs-ai-web/assets/css/tailwind.css`).

Tan accent (`#C9A389`) is the only saturated brand color. Light-first surface (Bone `#F1F1F1`). Display type Styrene A → Söhne → Inter fallback chain. Body Roboto, mono JetBrains Mono. See `/brand` route in `frontend-web` for the live token demo.

## Workflow engine

We do not use Inngest. We run **Celery + Redis** with a custom Django durable layer (`automations` app) that owns `Automation` / `AutomationRun` / `AutomationStepRun` / `HitlRequest` and a "run advancer" Celery task. See [PLAN.md §7](./PLAN.md#7-automation-engine-architecture-revised--celery--custom-django-durable-layer).

## License

All rights reserved — Offside Labs.
