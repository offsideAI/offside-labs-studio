from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "first_name",
            "last_name",
            "primary_email",
            "phones",
            "title",
            "company",
            "owner",
            "lifecycle_stage",
            "source",
            "custom",
            "tags",
            "created_by",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at", "deleted_at")
