# backend/

Django + DRF + Celery backend for Offside CRM. Deploys to **Digital Ocean App Platform** as three components: `web` (gunicorn), `worker` (celery), `beat` (celery-beat). See [PLAN.md §7](../PLAN.md#7-automation-engine-architecture-revised--celery--custom-django-durable-layer) for the workflow runtime architecture.

## Local dev (Docker — recommended)

From the repo root:

```bash
pnpm backend:up        # docker compose: postgres + redis + django web + worker + beat
pnpm backend:down      # tear down
```

Then visit:

| URL | What |
|---|---|
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/api/schema/` | OpenAPI 3.1 JSON |
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/health/live/` | Liveness probe |
| `http://localhost:8000/api/health/ready/` | Readiness probe (Postgres + Redis check) |

## Local dev (manual)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

cp .env.sample .env       # edit if needed
export $(grep -v '^#' .env | xargs)

python manage.py migrate
python manage.py runserver

# In separate shells:
celery -A offside_crm worker -l info
celery -A offside_crm beat -l info
```

## Deployment

`Procfile`-driven, mirroring SaucyCart's deployment posture:

```
web:     gunicorn offside_crm.wsgi --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --preload --log-file -
worker:  celery -A offside_crm worker -l info --concurrency 2
beat:    celery -A offside_crm beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
release: python manage.py migrate --noinput
```

DO App Platform reads the `Procfile` and provisions one component per process. Required env vars in production: see `.env.sample`.

## Workflow engine

The `apps/automations` Django app (lands in M7) owns:

- `Automation`, `AutomationRun`, `AutomationStepRun`, `HitlRequest`, `AgentPolicy` models.
- A `run_advancer(run_id)` Celery task that walks the workflow graph durably.
- Idempotency keyed by `(run_id, step_id, attempt)`.
- A "wake-up sweep" Beat task that re-enqueues advancers for delayed/waiting runs.

See PLAN.md §7 for the architecture diagram.

## Conventions

- All Django apps live under `apps/`. Each is workspace-scoped via the `WorkspaceScopedMixin` (lands in M2).
- Tests use `pytest-django`. Run with `pytest`.
- Lint with `ruff check .` and `ruff format .`.
- Type-check with `mypy .`.
