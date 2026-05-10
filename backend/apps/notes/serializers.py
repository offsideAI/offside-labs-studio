from rest_framework import serializers

from .models import NOTE_RELATABLE, Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = (
            "id",
            "body_md",
            "related_type",
            "related_id",
            "author",
            "edit_log",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "author", "edit_log", "created_at", "updated_at", "deleted_at")

    def validate_related_type(self, value: str) -> str:
        if value not in NOTE_RELATABLE:
            raise serializers.ValidationError(
                f"Notes can only attach to: {', '.join(sorted(NOTE_RELATABLE))}."
            )
        return value
