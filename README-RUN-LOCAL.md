# README-RUN-LOCAL.md — Run OffsideStudio locally

> Three-terminal recipe for running the whole stack — backend (Django + Celery + Postgres + Redis, all dockerized) + frontend (Next.js 15 on `:3000`) — and walking the demo. Pairs with [DEMO.md](./DEMO.md) for the on-stage script.

---

## Prerequisites

- **Docker Desktop** (or any Docker engine + Compose v2). Backend stack runs entirely in containers.
- **Node 20+** and **pnpm 9+**. The frontend is a pnpm workspaces monorepo.
- (Optional) `ANTHROPIC_API_KEY` — needed only if you want to demo the Describe-in-English panel.

You do **not** need a local Python install at all to run the demo. The Dockerfile bakes Python 3.12 + all deps into the image.

### If you want a local Python venv (editor autocomplete only)

The backend pins **Python 3.12** in four coordinated places: `backend/.python-version`, `backend/Dockerfile`, `backend/pyproject.toml` (`[project] requires-python = ">=3.12,<3.14"`), and `.github/workflows/ci.yml`. macOS system Python (3.9) won't satisfy the pins — `pip install` will refuse with a clear error.

Easiest way to get matched Python locally:

```bash
# Option A — pyenv (respects backend/.python-version automatically)
brew install pyenv
pyenv install 3.12.7
cd backend && pyenv local 3.12.7   # picks up the .python-version file

# Option B — asdf
brew install asdf
asdf plugin add python
asdf install python 3.12.7
cd backend && asdf local python 3.12.7

# Option C — direct Homebrew
brew install python@3.12

# Option D — mise (modern asdf-compatible replacement)
brew install mise
cd backend && mise use python@3.12
```

Then create the venv against 3.12:

```bash
cd backend
rm -rf venv                  # ← important; see "Stale venv symlinks" below
python3.12 -m venv venv      # or `python -m venv venv` if your shell picked up the version manager
source venv/bin/activate
python --version             # confirms 3.12.x
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

> **⚠ Stale venv symlinks — why `rm -rf venv` matters before re-creating.**
>
> If you previously ran `python3.9 -m venv venv` (or `python3 -m venv venv` on a system whose `python3` is 3.9), then re-ran `python3.12 -m venv venv` *on top* of it, the venv module will **not** replace the existing `python` / `python3` / `python3.9` symlinks. It'll only add the missing `python3.12` link and refresh `pyvenv.cfg`. Result: `python --version` follows the stale 3.9 symlink, even though `venv/bin/python3.12 --version` correctly says 3.12.x.
>
> Diagnostic — peek at the mtimes inside `venv/bin/`:
> ```bash
> ls -lT venv/bin/python*
> ```
> If `python`, `python3`, `python3.9` are stamped earlier than `python3.12` and `pip` / `activate`, you've hit this. They'll never converge until you blow the venv away.
>
> Fix:
> ```bash
> deactivate 2>/dev/null
> rm -rf venv
> /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv   # absolute path skips any PATH ambiguity
> source venv/bin/activate
> python --version   # should now print 3.12.x — not 3.9
> ```

If you're stuck on 3.9 (e.g., locked corporate machine), see `backend/requirements-dev.txt` — the `ipython` pin has a 3.9-compatible fallback comment. Other dev deps may also need relaxation.

---

## One-time setup

```bash
cd /Users/coder/repos/offsideai/githubrepos_workspace_active_1/offside-labs-studio
```

### 1. Backend `.env`

If `backend/.env` doesn't exist, create it:

```bash
cat > backend/.env <<'EOF'
DJANGO_SECRET_KEY=local-dev-only-do-not-use-in-prod
DATABASE_URL=postgres://offside:dev_only_password@db:5432/offside_crm
REDIS_URL=redis://redis:6379/0
ACCOUNT_EMAIL_VERIFICATION=optional
ANTHROPIC_API_KEY=sk-ant-...   # optional, omit if not demoing Describe-in-English
EOF
```

### 2. Install JS workspace deps (at the repo root)

```bash
pnpm install
```

This is a **pnpm workspaces** monorepo. `pnpm install` from the root resolves the entire workspace graph — `frontend-web` and its 5 sibling packages (`@offside/ui`, `@offside/ai`, `@offside/api-client`, `@offside/auth-utils`, `@offside/workflows-sdk`) all get their deduped deps via symlinks into a hoisted `node_modules`. Don't run `pnpm install` inside `frontend-web/` — the workspace pattern wants the root.

---

## Start the stack — three terminals

### Terminal 1 — backend stack (keep running)

```bash
pnpm backend:up
```

Boots Postgres + pgvector + Redis + Django web + Celery worker + Celery Beat. Wait until you see `Watching for file changes` (~15s on first run, image build takes longer).

### Terminal 2 — migrate + seed (one-time)

```bash
# Apply all migrations (incl. marketplace 0001+0002, ai 0001, automations 0002..0005).
pnpm backend:migrate

# Seed the marketplace catalog — 15 agents incl. the demo hero.
docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.marketplace

# Seed the demo workspace — acme-demo + owner user + 8 companies + 20 contacts + 12 deals + 5 tasks + 3 notes.
docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.demo_workspace

# Optional: confirm the backend tests pass (~30s).
pnpm backend:test
```

Both seed scripts are **idempotent** — re-running upserts by stable identifier (slug for agents; email/slug/name for the demo workspace).

### Terminal 3 — frontend dev server (keep running)

```bash
pnpm dev
```

Next.js boots on `http://localhost:3000`. (The placeholder Crunch / Design / Director surfaces also start on `:3001` / `:3002` / `:3003` — ignore them; they're 10-line shells.)

---

## Open the app + walk the demo

1. Browse to **`http://localhost:3000`**.
2. Click **Sign in**.
3. Log in as **`demo@offside.ai`** / **`DemoOnly123!`**.
4. You land in `/acme-demo` — the demo workspace home.

Walk the **5-minute DEMO.md narrative**:

1. **Sidebar** → click **Agent Marketplace** (★★).
2. Click into 🚀 **Ecommerce Conversion Funnel Optimizer** (the top card).
3. **Install to workspace**. You'll land in the Agent Design Studio with v1 already published.
4. Click **Run**.
5. Click the most recent run row in the footer → the Run Inspector opens with 10 step cards.
6. Expand `n2` (Launch marketing campaign), `n3` (AEO content seed — note `linked_to_campaign_status: 200` resolved live from `{{ n2.status_code }}`), `n6` (Create funnel company record — returned a real `company_id`), `n7` (Queue email task — `related_id` templated from `{{ n6.company_id }}`).
7. Switch to **Companies** in the sidebar — find **Acme Demo Funnel · 200** and click in. Three auto-queued tasks + the deployment-summary note are visible.

---

## Rebuilding the Docker image after backend deps change

The compose file bind-mounts `./backend → /app`, so **source-code changes** (settings, models, views, migrations, seed scripts) are picked up immediately by Django's autoreloader — no image rebuild needed.

But **installed Python packages** live inside the image at `/usr/local/lib/python3.12/site-packages/`, *not* in `/app`. So whenever `backend/requirements.txt` (or the `Dockerfile` itself) changes, you must rebuild:

```bash
# In Terminal 1, Ctrl-C to stop the running stack first if it's still up.

# Option A — rebuild then start:
docker compose -f backend/docker-compose.yml build
pnpm backend:up

# Option B — rebuild + start in one shot:
docker compose -f backend/docker-compose.yml up --build
```

The rebuild takes ~30–60s on a warm Docker cache (only the `pip install` layer reruns; the python:3.12-slim base image stays cached).

**When to rebuild** — anytime you see:
- A `ModuleNotFoundError: No module named '<x>'` from Django/Celery startup.
- Changes to `backend/requirements.txt`.
- Changes to `backend/Dockerfile`.

If a freshly-rebuilt image *still* errors with `ModuleNotFoundError`, the missing package isn't in `requirements.txt` yet — add it, then rebuild again.

---

## Pre-stage hash check (optional)

Run before going on stage to verify everything is wired up:

```bash
docker compose -f backend/docker-compose.yml exec web python manage.py shell -c "
from apps.marketplace.models import MarketplaceAgent
from apps.workspaces.models import Workspace
from apps.contacts.models import Contact
from apps.companies.models import Company
ws = Workspace.objects.get(slug='acme-demo')
print(
    'agents=', MarketplaceAgent.objects.count(),
    'hero=', MarketplaceAgent.objects.filter(slug='ecommerce-conversion-funnel-optimizer').exists(),
    'contacts=', Contact.objects.filter(workspace=ws).count(),
    'companies=', Company.objects.filter(workspace=ws).count(),
)
"
# Expected: agents= 15 hero= True contacts= 20 companies= 8
```

Plus a JWT round-trip:

```bash
curl -s -X POST http://localhost:8000/api/auth/login/ \
    -H 'Content-Type: application/json' \
    -d '{"email":"demo@offside.ai","password":"DemoOnly123!"}' \
    | head -c 80
# Expected: a JSON blob starting "{\"access\":\"eyJ0..."
```

---

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `python --version` in the venv reports 3.9 even after `python3.12 -m venv venv` | Stale `python` / `python3` symlinks from a previous 3.9 venv that wasn't deleted first | `deactivate; rm -rf venv; /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv; source venv/bin/activate; python --version` (see the "Stale venv symlinks" callout above) |
| `unknown shorthand flag: 'f' in -f` from `docker compose -f …` | Compose v2 plugin not installed | `brew install docker-compose && mkdir -p ~/.docker/cli-plugins && ln -sfn /opt/homebrew/lib/docker/cli-plugins/docker-compose ~/.docker/cli-plugins/docker-compose` |
| `service "web" is not running` from `pnpm backend:migrate` | Stack wasn't started first | Run `pnpm backend:up` in Terminal 1 *first*; wait for the Django "Starting development server at …" line; then run migrate in Terminal 2 |
| `WARN The "rb" variable is not set` (or any `WARN The "x" variable is not set`) | `backend/.env` has a literal `$x` in a value that Docker Compose tries to interpolate | Escape the `$` as `$$` in `backend/.env`, e.g. `ANTHROPIC_API_KEY=sk-ant-…$$rb…`, or remove the offending line |
| Container exits with `ModuleNotFoundError: No module named '<x>'` | Missing pin in `backend/requirements.txt` | Add the package to `backend/requirements.txt`, then rebuild — see "Rebuilding the Docker image after backend deps change" above |
| `ImproperlyConfigured: You must include 'rest_framework.authtoken' …` | `REST_AUTH` config missing `TOKEN_MODEL: None` | Already fixed in `settings/base.py`. If you ever see this again, confirm `REST_AUTH["TOKEN_MODEL"] = None` is present |
| `pnpm install` errors on `@xyflow/react` | Lockfile stale | `pnpm install --no-frozen-lockfile` |
| `pnpm dev` errors with TypeScript compile messages | Type drift since last typecheck | Paste the error in chat with me — I'll fix in-line |
| `pnpm backend:up` errors with `cannot find module 'turbo'` | Mixed-up command | `pnpm backend:up` is correct; not a turbo task |
| `backend:migrate` shows `no migrations to apply` | Already current | Continue to the seed step |
| Seed errors `apps.workspaces.models.Workspace.DoesNotExist` | Migrations not applied | Re-run `pnpm backend:migrate` |
| Marketplace grid is empty | Seed didn't run | Re-run `docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.marketplace` |
| Login fails with 401 | EmailAddress row missing | Re-run `docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.demo_workspace` (idempotent) |
| Install endpoint returns 401 | Workspace context not loaded | Refresh the browser tab after login |
| Hero agent's run shows `failed` | httpbin.org unreachable from container | `docker compose -f backend/docker-compose.yml exec web curl -X POST https://httpbin.org/post -d '{}'` to confirm — if blocked, replace the placeholder URLs in the seed with `https://postman-echo.com/post` and re-seed |
| Recent run row never appears in the editor footer | Celery worker container down | `docker compose -f backend/docker-compose.yml ps` — `worker` should be `Up`. If not: `docker compose -f backend/docker-compose.yml restart worker` |
| Describe-in-English panel hangs | `ANTHROPIC_API_KEY` missing / invalid / rate-limited | Set the key in `backend/.env` and restart `backend:up`, or skip Step 4 of DEMO.md |
| Postgres won't start with `port already in use` | Local Postgres on `:5432` | Stop your host Postgres or change the port mapping in `backend/docker-compose.yml` |
| Redis won't start with `port already in use` | Local Redis on `:6379` | Same — stop the host instance |
| `python manage.py shell -c …` exits with `KeyError: 'TERM'` | Shell allocation in non-interactive mode | Use `python manage.py shell --no-startup -c …` or run with `docker compose exec -T web` |

---

## Reset / cleanup

If state gets weird and you want a clean slate:

```bash
# Stop everything.
pnpm backend:down

# Nuke the Postgres volume (DESTRUCTIVE — wipes the demo workspace + all CRM data).
docker compose -f backend/docker-compose.yml down -v

# Then run the full setup again: pnpm backend:up → migrate → both seeds.
```

If you only want to re-seed (keep the schema, replace catalog/demo data):

```bash
docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.marketplace
docker compose -f backend/docker-compose.yml exec web python -m tools.seeds.demo_workspace
```

Both are idempotent, so running them on existing data updates fields instead of duplicating rows.

---

## Useful shortcuts

```bash
# Live tail backend logs.
docker compose -f backend/docker-compose.yml logs -f web worker beat

# Open Django shell in the running container.
docker compose -f backend/docker-compose.yml exec web python manage.py shell_plus

# Open Django admin in the browser.
# http://localhost:8000/admin/  (create a superuser first via `createsuperuser`)
docker compose -f backend/docker-compose.yml exec web python manage.py createsuperuser

# OpenAPI schema (for codegen / inspection).
curl http://localhost:8000/api/schema/ | jq .
```

---

## Where to look when something breaks

- **Backend logs** (Terminal 1) — Django + Celery output streams here. Most Python errors land here first.
- **Frontend logs** (Terminal 3) — Next.js compile errors, runtime errors, hydration mismatches.
- **Run Inspector** in the app (`/[workspace]/automations/[id]/runs/[runId]/`) — every workflow step's input/output/cost/error/idempotency_key.
- **Django admin** (`/admin/`) — direct DB access for `MarketplaceAgent`, `Automation`, `AutomationRun`, `WorkspaceAgentInstall`, `WebhookEndpoint`, `ScheduleTrigger`, `FormEndpoint`, `AICall`.
- **`docker compose ps`** — health of the 5 backend containers (`web`, `worker`, `beat`, `db`, `redis`).

---

*Last revised: 2026-05. Aligned with PRD.md v3.2 and ROADMAP.md Revision 14. Stage-presentation script lives in [DEMO.md](./DEMO.md).*
