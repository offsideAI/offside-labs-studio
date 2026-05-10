from rest_framework import serializers

from .models import CustomFieldDef


class CustomFieldDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldDef
        fields = (
            "id",
            "entity_type",
            "key",
            "label",
            "type",
            "options",
            "required",
            "indexed",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
