"""Seed a polished demo workspace for stage demos / conference talks.

Run from the backend container:

    docker compose -f backend/docker-compose.yml exec web \
        python -m tools.seeds.demo_workspace

Idempotent: re-running upserts by stable identifier (slug / email /
name) so the data stays clean across re-seeds.

Creates:
- 1 demo owner (`demo@offside.ai` / `DemoOnly123!`).
- 1 workspace (`Acme Sales` / slug=`acme-demo`) owned by the demo user.
- 1 default Pipeline using the standard 6-stage layout.
- 8 companies across realistic industries.
- 20 contacts (~2-3 per company on average).
- 12 deals distributed across the 6 pipeline stages.
- 5 tasks (mix of open + completed) attached to contacts/deals.
- 3 notes attached to contacts/deals.

Does **not** pre-install marketplace agents — the demo opener is "install
your first agent live from the Marketplace." Make sure to run
`python -m tools.seeds.marketplace` first so the catalog has agents to install.
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any

# Make `apps.*` importable when run as `python -m tools.seeds.demo_workspace`
# from the repo root or from inside the backend container.
_BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

import django  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "offside_crm.settings.dev")
django.setup()

from allauth.account.models import EmailAddress  # noqa: E402
from django.utils import timezone as django_tz  # noqa: E402

from apps.companies.models import Company  # noqa: E402
from apps.contacts.models import Contact  # noqa: E402
from apps.deals.models import Deal, Pipeline, default_pipeline_stages  # noqa: E402
from apps.notes.models import Note  # noqa: E402
from apps.tasks.models import Task  # noqa: E402
from apps.users.models import User  # noqa: E402
from apps.workspaces.models import Membership, Role, Workspace  # noqa: E402


DEMO_EMAIL = "demo@offside.ai"
DEMO_PASSWORD = "DemoOnly123!"
DEMO_WORKSPACE_SLUG = "acme-demo"
DEMO_WORKSPACE_NAME = "Acme Sales"


COMPANIES: list[dict[str, Any]] = [
    {"name": "Acme Corp", "domain": "acme.example", "industry": "Manufacturing", "size_band": "51-200"},
    {"name": "Globex Industries", "domain": "globex.example", "industry": "Industrial", "size_band": "201-1000"},
    {"name": "Initech", "domain": "initech.example", "industry": "Software", "size_band": "11-50"},
    {"name": "Massive Dynamic", "domain": "massivedynamic.example", "industry": "R&D", "size_band": "1000+"},
    {"name": "Soylent Foods", "domain": "soylent.example", "industry": "Consumer Goods", "size_band": "51-200"},
    {"name": "Stark Industries", "domain": "stark.example", "industry": "Energy", "size_band": "1000+"},
    {"name": "Wonka Chocolatiers", "domain": "wonka.example", "industry": "Consumer Goods", "size_band": "201-1000"},
    {"name": "Wayne Enterprises", "domain": "wayne.example", "industry": "Conglomerate", "size_band": "1000+"},
]


CONTACTS: list[dict[str, Any]] = [
    {"first_name": "Ada", "last_name": "Lovelace", "primary_email": "ada@acme.example", "title": "VP Engineering", "company": "Acme Corp", "lifecycle_stage": "customer"},
    {"first_name": "Linus", "last_name": "Pauling", "primary_email": "linus@acme.example", "title": "Director of Ops", "company": "Acme Corp", "lifecycle_stage": "customer"},
    {"first_name": "Grace", "last_name": "Hopper", "primary_email": "grace@globex.example", "title": "CTO", "company": "Globex Industries", "lifecycle_stage": "opportunity"},
    {"first_name": "Alan", "last_name": "Turing", "primary_email": "alan@globex.example", "title": "Head of AI", "company": "Globex Industries", "lifecycle_stage": "opportunity"},
    {"first_name": "Donald", "last_name": "Knuth", "primary_email": "don@initech.example", "title": "Founder", "company": "Initech", "lifecycle_stage": "lead"},
    {"first_name": "Margaret", "last_name": "Hamilton", "primary_email": "margaret@initech.example", "title": "VP Product", "company": "Initech", "lifecycle_stage": "lead"},
    {"first_name": "Ken", "last_name": "Thompson", "primary_email": "ken@massivedynamic.example", "title": "Distinguished Engineer", "company": "Massive Dynamic", "lifecycle_stage": "opportunity"},
    {"first_name": "Dennis", "last_name": "Ritchie", "primary_email": "dennis@massivedynamic.example", "title": "Principal Architect", "company": "Massive Dynamic", "lifecycle_stage": "opportunity"},
    {"first_name": "Barbara", "last_name": "Liskov", "primary_email": "barbara@soylent.example", "title": "Head of Platform", "company": "Soylent Foods", "lifecycle_stage": "customer"},
    {"first_name": "Edsger", "last_name": "Dijkstra", "primary_email": "edsger@soylent.example", "title": "VP Engineering", "company": "Soylent Foods", "lifecycle_stage": "customer"},
    {"first_name": "Anita", "last_name": "Borg", "primary_email": "anita@stark.example", "title": "Director of R&D", "company": "Stark Industries", "lifecycle_stage": "opportunity"},
    {"first_name": "Tim", "last_name": "Berners-Lee", "primary_email": "tim@stark.example", "title": "Chief Scientist", "company": "Stark Industries", "lifecycle_stage": "customer"},
    {"first_name": "John", "last_name": "von Neumann", "primary_email": "john@stark.example", "title": "VP Strategy", "company": "Stark Industries", "lifecycle_stage": "lead"},
    {"first_name": "Radia", "last_name": "Perlman", "primary_email": "radia@wonka.example", "title": "VP Network", "company": "Wonka Chocolatiers", "lifecycle_stage": "lead"},
    {"first_name": "Vint", "last_name": "Cerf", "primary_email": "vint@wonka.example", "title": "Head of Infrastructure", "company": "Wonka Chocolatiers", "lifecycle_stage": "opportunity"},
    {"first_name": "Bjarne", "last_name": "Stroustrup", "primary_email": "bjarne@wayne.example", "title": "Chief Architect", "company": "Wayne Enterprises", "lifecycle_stage": "customer"},
    {"first_name": "Brendan", "last_name": "Eich", "primary_email": "brendan@wayne.example", "title": "VP Engineering", "company": "Wayne Enterprises", "lifecycle_stage": "customer"},
    {"first_name": "Brian", "last_name": "Kernighan", "primary_email": "brian@wayne.example", "title": "Director of R&D", "company": "Wayne Enterprises", "lifecycle_stage": "opportunity"},
    {"first_name": "Rich", "last_name": "Hickey", "primary_email": "rich@initech.example", "title": "Staff Engineer", "company": "Initech", "lifecycle_stage": "lead"},
    {"first_name": "Joe", "last_name": "Armstrong", "primary_email": "joe@globex.example", "title": "VP Reliability", "company": "Globex Industries", "lifecycle_stage": "opportunity"},
]


DEALS: list[dict[str, Any]] = [
    {"name": "Acme — Q3 expansion seat upgrade", "company": "Acme Corp", "contact": "ada@acme.example", "stage_id": "closed_won", "value_cents": 4_800_000},
    {"name": "Acme — managed migration services", "company": "Acme Corp", "contact": "linus@acme.example", "stage_id": "demo", "value_cents": 1_200_000},
    {"name": "Globex — multi-region rollout", "company": "Globex Industries", "contact": "grace@globex.example", "stage_id": "negotiation", "value_cents": 9_600_000},
    {"name": "Globex — AI-platform add-on", "company": "Globex Industries", "contact": "alan@globex.example", "stage_id": "demo", "value_cents": 3_400_000},
    {"name": "Initech — pilot license", "company": "Initech", "contact": "don@initech.example", "stage_id": "qualified", "value_cents": 600_000},
    {"name": "Massive Dynamic — RFP response", "company": "Massive Dynamic", "contact": "ken@massivedynamic.example", "stage_id": "qualified", "value_cents": 12_000_000},
    {"name": "Massive Dynamic — security review fee", "company": "Massive Dynamic", "contact": "dennis@massivedynamic.example", "stage_id": "lead", "value_cents": 250_000},
    {"name": "Soylent — yearly renewal", "company": "Soylent Foods", "contact": "barbara@soylent.example", "stage_id": "closed_won", "value_cents": 5_400_000},
    {"name": "Stark — energy platform pilot", "company": "Stark Industries", "contact": "anita@stark.example", "stage_id": "negotiation", "value_cents": 18_000_000},
    {"name": "Stark — observability add-on", "company": "Stark Industries", "contact": "tim@stark.example", "stage_id": "demo", "value_cents": 2_100_000},
    {"name": "Wonka — onboarding services", "company": "Wonka Chocolatiers", "contact": "vint@wonka.example", "stage_id": "qualified", "value_cents": 900_000},
    {"name": "Wayne — strategic deployment", "company": "Wayne Enterprises", "contact": "bjarne@wayne.example", "stage_id": "closed_won", "value_cents": 22_000_000},
]


TASKS: list[dict[str, Any]] = [
    {"title": "Send follow-up after demo", "related_email": "grace@globex.example", "related_type": "contact", "priority": "high", "status": "open"},
    {"title": "Prep technical scorecard", "related_email": "ken@massivedynamic.example", "related_type": "contact", "priority": "high", "status": "open"},
    {"title": "Schedule security review", "related_email": "dennis@massivedynamic.example", "related_type": "contact", "priority": "medium", "status": "open"},
    {"title": "Send renewal quote", "related_email": "barbara@soylent.example", "related_type": "contact", "priority": "medium", "status": "done"},
    {"title": "Call to confirm rollout date", "related_email": "anita@stark.example", "related_type": "contact", "priority": "high", "status": "open"},
]


NOTES: list[dict[str, Any]] = [
    {
        "related_email": "grace@globex.example",
        "related_type": "contact",
        "body_md": "Demo went well. Grace asked deep questions about idempotency + multi-region. Next: send the architecture deck + intro to our SRE.",
    },
    {
        "related_email": "ken@massivedynamic.example",
        "related_type": "contact",
        "body_md": "RFP response due **Friday EOD**. Security questionnaire is the long pole — need answers from the platform team by Thursday.",
    },
    {
        "related_email": "anita@stark.example",
        "related_type": "contact",
        "body_md": "Anita confirmed budget for the pilot. Procurement has 30-day SLA on contracts. **Watch the renewal terms** — they pushed back on auto-renew last time.",
    },
]


def upsert_demo_user() -> User:
    user, created = User.objects.get_or_create(
        email=DEMO_EMAIL,
        defaults={"is_active": True},
    )
    # Force the password every run so the demo presenter always has known creds.
    user.set_password(DEMO_PASSWORD)
    user.is_active = True
    user.save(update_fields=["password", "is_active"])
    # allauth needs a verified EmailAddress so dj-rest-auth login works without
    # mandatory verification kicking in.
    EmailAddress.objects.update_or_create(
        user=user,
        email=DEMO_EMAIL,
        defaults={"verified": True, "primary": True},
    )
    print(f"  user: {'created' if created else 'updated'} {DEMO_EMAIL}")
    return user


def upsert_workspace(owner: User) -> Workspace:
    workspace, created = Workspace.objects.get_or_create(
        slug=DEMO_WORKSPACE_SLUG,
        defaults={"name": DEMO_WORKSPACE_NAME, "created_by": owner},
    )
    Membership.objects.get_or_create(
        workspace=workspace, user=owner, defaults={"role": Role.OWNER}
    )
    print(
        f"  workspace: {'created' if created else 'existed'} "
        f"{DEMO_WORKSPACE_NAME} (slug={DEMO_WORKSPACE_SLUG})"
    )
    return workspace


def upsert_pipeline(workspace: Workspace, owner: User) -> Pipeline:
    pipeline, created = Pipeline.objects.get_or_create(
        workspace=workspace,
        name="Sales pipeline",
        defaults={
            "stages": default_pipeline_stages(),
            "is_default": True,
            "created_by": owner,
        },
    )
    print(f"  pipeline: {'created' if created else 'existed'} {pipeline.name}")
    return pipeline


def upsert_companies(workspace: Workspace, owner: User) -> dict[str, Company]:
    by_name: dict[str, Company] = {}
    for spec in COMPANIES:
        company, created = Company.objects.get_or_create(
            workspace=workspace,
            name=spec["name"],
            defaults={
                "domain": spec["domain"],
                "industry": spec["industry"],
                "size_band": spec["size_band"],
                "created_by": owner,
            },
        )
        if not created:
            # Refresh fields on re-seed so updates to the seed file propagate.
            company.domain = spec["domain"]
            company.industry = spec["industry"]
            company.size_band = spec["size_band"]
            company.save(update_fields=["domain", "industry", "size_band"])
        by_name[spec["name"]] = company
    print(f"  companies: {len(by_name)} total")
    return by_name


def upsert_contacts(
    workspace: Workspace, owner: User, companies: dict[str, Company]
) -> dict[str, Contact]:
    by_email: dict[str, Contact] = {}
    for spec in CONTACTS:
        company = companies.get(spec["company"])
        contact, created = Contact.objects.get_or_create(
            workspace=workspace,
            primary_email=spec["primary_email"],
            defaults={
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
                "title": spec["title"],
                "lifecycle_stage": spec["lifecycle_stage"],
                "company": company,
                "created_by": owner,
            },
        )
        if not created:
            contact.first_name = spec["first_name"]
            contact.last_name = spec["last_name"]
            contact.title = spec["title"]
            contact.lifecycle_stage = spec["lifecycle_stage"]
            contact.company = company
            contact.save(
                update_fields=["first_name", "last_name", "title", "lifecycle_stage", "company"]
            )
        by_email[spec["primary_email"]] = contact
    print(f"  contacts: {len(by_email)} total")
    return by_email


def upsert_deals(
    workspace: Workspace,
    owner: User,
    pipeline: Pipeline,
    companies: dict[str, Company],
    contacts: dict[str, Contact],
) -> int:
    count = 0
    today = date.today()
    for i, spec in enumerate(DEALS):
        company = companies.get(spec["company"])
        contact = contacts.get(spec["contact"])
        # Stagger expected close dates across the next 90 days so the kanban
        # looks lived-in.
        expected_close = today + timedelta(days=7 * (i + 1))
        deal, created = Deal.objects.get_or_create(
            workspace=workspace,
            name=spec["name"],
            defaults={
                "pipeline": pipeline,
                "stage_id": spec["stage_id"],
                "value_cents": spec["value_cents"],
                "currency": "USD",
                "expected_close": expected_close,
                "company": company,
                "contact": contact,
                "owner": owner,
                "created_by": owner,
            },
        )
        if not created:
            deal.stage_id = spec["stage_id"]
            deal.value_cents = spec["value_cents"]
            deal.expected_close = expected_close
            deal.company = company
            deal.contact = contact
            deal.save(
                update_fields=[
                    "stage_id", "value_cents", "expected_close", "company", "contact"
                ]
            )
        count += 1
    print(f"  deals: {count} total")
    return count


def upsert_tasks(workspace: Workspace, owner: User, contacts: dict[str, Contact]) -> int:
    count = 0
    for spec in TASKS:
        contact = contacts.get(spec["related_email"])
        if contact is None:
            continue
        defaults: dict[str, Any] = {
            "related_type": spec["related_type"],
            "related_id": contact.id,
            "priority": spec["priority"],
            "status": spec["status"],
            "created_by": owner,
            "owner": owner,
        }
        if spec["status"] == "done":
            defaults["completed_at"] = django_tz.now()
        task, created = Task.objects.get_or_create(
            workspace=workspace,
            title=spec["title"],
            defaults=defaults,
        )
        count += 1
    print(f"  tasks: {count} total")
    return count


def upsert_notes(workspace: Workspace, owner: User, contacts: dict[str, Contact]) -> int:
    count = 0
    for spec in NOTES:
        contact = contacts.get(spec["related_email"])
        if contact is None:
            continue
        # Idempotency for notes: lookup by (workspace, related, first 64 chars of body).
        existing = Note.objects.filter(
            workspace=workspace,
            related_type=spec["related_type"],
            related_id=contact.id,
            body_md__startswith=spec["body_md"][:64],
        ).first()
        if existing is None:
            Note.objects.create(
                workspace=workspace,
                related_type=spec["related_type"],
                related_id=contact.id,
                body_md=spec["body_md"],
                author=owner,
            )
        count += 1
    print(f"  notes: {count} total")
    return count


def main() -> None:
    print("seeding demo workspace…")
    user = upsert_demo_user()
    workspace = upsert_workspace(user)
    pipeline = upsert_pipeline(workspace, user)
    companies = upsert_companies(workspace, user)
    contacts = upsert_contacts(workspace, user, companies)
    upsert_deals(workspace, user, pipeline, companies, contacts)
    upsert_tasks(workspace, user, contacts)
    upsert_notes(workspace, user, contacts)
    print()
    print(f"demo workspace ready — slug={DEMO_WORKSPACE_SLUG}")
    print(f"  log in as {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print(
        "  marketplace agents are *not* pre-installed — run "
        "`python -m tools.seeds.marketplace` first so they're in the catalog, "
        "then install one live as the demo opener."
    )


if __name__ == "__main__":
    main()
