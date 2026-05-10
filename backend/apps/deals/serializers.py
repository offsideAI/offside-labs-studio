from rest_framework import serializers

from .models import Deal, Pipeline


class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = ("id", "name", "stages", "is_default", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = (
            "id",
            "name",
            "pipeline",
            "stage_id",
            "value_cents",
            "currency",
            "expected_close",
            "contact",
            "company",
            "owner",
            "custom",
            "tags",
            "created_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at", "deleted_at")
