from rest_framework import serializers

from apps.activities.types import RelatedType

from .models import TASK_RELATABLE, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "due_at",
            "related_type",
            "related_id",
            "status",
            "priority",
            "owner",
            "custom",
            "completed_at",
            "created_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "completed_at", "created_by", "created_at", "updated_at", "deleted_at")

    def validate_related_type(self, value: str) -> str:
        if value not in TASK_RELATABLE:
            raise serializers.ValidationError(
                f"Tasks can only be attached to: {', '.join(sorted(TASK_RELATABLE))}."
            )
        return value
