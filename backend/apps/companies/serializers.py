from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "domain",
            "size_band",
            "industry",
            "owner",
            "custom",
            "tags",
            "created_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at", "deleted_at")
