"""DRF serializers for the auth surface.

`CustomRegisterSerializer` strips the username field that dj-rest-auth's
default `RegisterSerializer` insists on, and adds a `full_name` field.
`UserSerializer` is what gets returned by GET /api/auth/user/.
"""

from __future__ import annotations

from typing import Any

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "avatar_url", "date_joined")
        read_only_fields = ("id", "email", "date_joined")


class CustomRegisterSerializer(RegisterSerializer):
    """Email-based registration. No username field."""

    username = None
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def get_cleaned_data(self) -> dict[str, Any]:
        data = super().get_cleaned_data()
        data["full_name"] = self.validated_data.get("full_name", "")
        return data

    def custom_signup(self, request, user) -> None:  # type: ignore[no-untyped-def]
        full_name = self.validated_data.get("full_name", "")
        if full_name:
            user.full_name = full_name
            user.save(update_fields=["full_name"])
