"""URL routes for /api/workspaces/* and the public invitation endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    InvitationViewSet,
    MembershipViewSet,
    WorkspaceViewSet,
    accept_invitation,
    public_invitation_detail,
)

router = DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspace")
router.register(r"memberships", MembershipViewSet, basename="membership")
router.register(r"invitations", InvitationViewSet, basename="invitation")

urlpatterns = [
    # Public — used by the invitee's accept-invite landing page before they're logged in.
    path("invitations/<uuid:token>/", public_invitation_detail, name="invitation-public-detail"),
    # Authenticated — invitee accepts after signing up.
    path("invitations/<uuid:token>/accept/", accept_invitation, name="invitation-accept"),
    # Standard CRUD.
    path("", include(router.urls)),
]
