from django.contrib import admin

from .models import Invitation, Membership, Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "plan", "created_by", "created_at", "deleted_at")
    list_filter = ("plan",)
    search_fields = ("name", "slug", "created_by__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role", "joined_at", "deactivated_at")
    list_filter = ("role",)
    search_fields = ("user__email", "workspace__slug", "workspace__name")
    autocomplete_fields = ("workspace", "user")
    ordering = ("-joined_at",)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "workspace", "role", "invited_by", "created_at", "expires_at", "accepted_at")
    list_filter = ("role",)
    search_fields = ("email", "workspace__slug")
    readonly_fields = ("token", "created_at", "expires_at", "accepted_at")
    autocomplete_fields = ("workspace", "invited_by")
    ordering = ("-created_at",)
