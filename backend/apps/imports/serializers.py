from rest_framework import serializers

from .models import ImportRun


class ImportRunSerializer(serializers.ModelSerializer):
    progress_pct = serializers.SerializerMethodField()
    sample_rows = serializers.SerializerMethodField()
    headers = serializers.SerializerMethodField()

    class Meta:
        model = ImportRun
        fields = (
            "id",
            "entity_type",
            "file_name",
            "mapping",
            "status",
            "total_rows",
            "processed_rows",
            "error_rows",
            "errors",
            "headers",
            "sample_rows",
            "progress_pct",
            "created_at",
            "started_at",
            "finished_at",
        )
        read_only_fields = (
            "id",
            "status",
            "total_rows",
            "processed_rows",
            "error_rows",
            "errors",
            "created_at",
            "started_at",
            "finished_at",
        )

    def get_progress_pct(self, obj: ImportRun) -> int:
        if not obj.total_rows:
            return 0
        return int((obj.processed_rows / obj.total_rows) * 100)

    def get_headers(self, obj: ImportRun) -> list[str]:
        if not obj.raw_content:
            return []
        first_line = obj.raw_content.split("\n", 1)[0]
        import csv

        return next(csv.reader([first_line]))

    def get_sample_rows(self, obj: ImportRun) -> list[list[str]]:
        if not obj.raw_content:
            return []
        import csv
        from io import StringIO

        reader = csv.reader(StringIO(obj.raw_content))
        rows: list[list[str]] = []
        for index, row in enumerate(reader):
            if index == 0:
                continue  # skip header
            if index > 5:
                break
            rows.append(row)
        return rows
