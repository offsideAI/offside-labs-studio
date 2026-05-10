"""ViewSet + upload endpoint for CSV imports."""

from __future__ import annotations

import csv
from io import StringIO

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.workspaces.permissions import IsWorkspaceAdmin

from .mappings import suggest_mapping
from .models import ImportEntityType, ImportRun, ImportStatus
from .serializers import ImportRunSerializer
from .tasks import run_csv_import


class ImportRunViewSet(viewsets.ModelViewSet):
    serializer_class = ImportRunSerializer
    permission_classes = [IsWorkspaceAdmin]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return ImportRun.objects.none()
        return ImportRun.objects.for_workspace(workspace_id).select_related("created_by")

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):  # type: ignore[no-untyped-def]
        """Multipart upload of a CSV file. Returns the ImportRun with suggested mapping + sample rows."""
        workspace_id = getattr(request, "workspace_id", None)
        entity_type = request.data.get("entity_type", ImportEntityType.CONTACT)
        file_obj = request.data.get("file")

        if entity_type not in dict(ImportEntityType.choices):
            return Response({"detail": "invalid entity_type"}, status=status.HTTP_400_BAD_REQUEST)
        if not file_obj:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            raw_bytes = file_obj.read()
            raw_content = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response({"detail": "file must be UTF-8 CSV"}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.reader(StringIO(raw_content))
        try:
            headers = next(reader)
        except StopIteration:
            return Response({"detail": "empty CSV"}, status=status.HTTP_400_BAD_REQUEST)

        # Count remaining rows for progress reporting.
        total = sum(1 for _ in reader)

        run = ImportRun.objects.create(
            workspace_id=workspace_id,
            entity_type=entity_type,
            file_name=getattr(file_obj, "name", ""),
            raw_content=raw_content,
            mapping=suggest_mapping(headers, entity_type),
            total_rows=total,
            created_by=request.user,
        )
        return Response(self.get_serializer(run).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="commit")
    def commit(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Enqueue the Celery task. Mapping must already be saved on the run."""
        run = self.get_object()
        if run.status != ImportStatus.PENDING:
            return Response(
                {"detail": f"import is already {run.status}"},
                status=status.HTTP_409_CONFLICT,
            )
        if not run.mapping:
            return Response(
                {"detail": "mapping is empty — set columns before committing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        run_csv_import.delay(run.id)
        return Response(self.get_serializer(run).data)
