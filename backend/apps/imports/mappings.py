"""Heuristic column-header → field-name mapper.

M4 ships a deterministic header-name matcher. M11 swaps in a Claude
prompt (`imports.suggest_column_mapping.v1`) for messier real-world
headers. The deterministic version is documented + unit-testable, so
the upgrade path is "wrap this with the LLM call when the heuristic
returns no match."
"""

from __future__ import annotations

import re

# Standard fields per entity that the heuristic can populate. Custom
# fields land in `custom.<key>` — those mappings come from the user
# explicitly via the wizard.

CONTACT_FIELD_HINTS: dict[str, list[str]] = {
    "first_name": ["first_name", "first", "given_name", "fname"],
    "last_name": ["last_name", "last", "surname", "family_name", "lname"],
    "primary_email": ["email", "primary_email", "email_address", "work_email"],
    "title": ["title", "job_title", "position", "role"],
    "source": ["source", "lead_source", "channel"],
    "lifecycle_stage": ["lifecycle", "lifecycle_stage", "stage", "status"],
}

COMPANY_FIELD_HINTS: dict[str, list[str]] = {
    "name": ["name", "company", "company_name", "account", "account_name"],
    "domain": ["domain", "website", "url"],
    "industry": ["industry", "sector", "vertical"],
    "size_band": ["size", "size_band", "employees", "headcount"],
}

ENTITY_HINTS: dict[str, dict[str, list[str]]] = {
    "contact": CONTACT_FIELD_HINTS,
    "company": COMPANY_FIELD_HINTS,
}


def normalize(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def suggest_mapping(headers: list[str], entity_type: str) -> dict[str, str]:
    """Return a {column_index: field_name} mapping inferred from headers.

    Column indexes are stringified so the JSONField round-trips cleanly.
    Headers that don't match any known field are left out — the user can
    set them in the wizard before committing.
    """
    field_hints = ENTITY_HINTS.get(entity_type, {})
    mapping: dict[str, str] = {}
    for index, raw in enumerate(headers):
        normalized = normalize(raw)
        for field, hints in field_hints.items():
            if normalized in hints:
                mapping[str(index)] = field
                break
            if any(hint in normalized for hint in hints):
                mapping[str(index)] = field
                break
    return mapping
