"""Celery task that runs a CSV import to completion."""

from __future__ import annotations

import csv
from io import StringIO

from celery import shared_task
from django.utils import timezone

from apps.companies.models import Company
from apps.contacts.models import Contact

from .models import ImportEntityType, ImportRun, ImportStatus


@shared_task(name="imports.run_csv_import")
def run_csv_import(import_run_id: int) -> str:
    run = ImportRun.objects.select_related("workspace", "created_by").get(pk=import_run_id)
    run.status = ImportStatus.RUNNING
    run.started_at = timezone.now()
    run.processed_rows = 0
    run.error_rows = 0
    run.errors = []
    run.save(update_fields=["status", "started_at", "processed_rows", "error_rows", "errors"])

    reader = csv.reader(StringIO(run.raw_content))
    try:
        next(reader)  # skip header
    except StopIteration:
        run.status = ImportStatus.FAILED
        run.errors = [{"row": 0, "message": "CSV is empty."}]
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "errors", "finished_at"])
        return "failed: empty"

    mapping = {int(k): v for k, v in run.mapping.items()}
    is_contact = run.entity_type == ImportEntityType.CONTACT

    for row_index, row in enumerate(reader, start=2):  # row 1 was the header
        try:
            values = {field: (row[col_idx].strip() if col_idx < len(row) else "") for col_idx, field in mapping.items()}
            if is_contact:
                Contact.objects.create(
                    workspace=run.workspace,
                    created_by=run.created_by,
                    **{k: v for k, v in values.items() if v},
                )
            else:
                if not values.get("name"):
                    raise ValueError("Company `name` is required.")
                Company.objects.create(
                    workspace=run.workspace,
                    created_by=run.created_by,
                    **{k: v for k, v in values.items() if v},
                )
            run.processed_rows += 1
        except Exception as exc:  # noqa: BLE001 — we surface every per-row failure
            run.error_rows += 1
            run.errors.append(
                {
                    "row": row_index,
                    "message": f"{exc.__class__.__name__}: {exc}",
                }
            )

        if (row_index % 50) == 0:
            run.save(update_fields=["processed_rows", "error_rows", "errors"])

    run.status = ImportStatus.COMPLETE
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "processed_rows", "error_rows", "errors", "finished_at"])
    return f"complete: {run.processed_rows} ok, {run.error_rows} failed"
