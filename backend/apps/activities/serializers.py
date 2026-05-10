from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor_user.email", read_only=True, allow_null=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "kind",
            "actor_kind",
            "actor_user",
            "actor_email",
            "related_type",
            "related_id",
            "payload",
            "occurred_at",
        )
        read_only_fields = fields
