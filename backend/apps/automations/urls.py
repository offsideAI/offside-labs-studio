from rest_framework.routers import DefaultRouter

from .views import AutomationRunViewSet, AutomationVersionViewSet, AutomationViewSet

router = DefaultRouter()
router.register(r"automations", AutomationViewSet, basename="automation")
router.register(r"automation-runs", AutomationRunViewSet, basename="automation-run")
router.register(
    r"automation-versions", AutomationVersionViewSet, basename="automation-version"
)

urlpatterns = router.urls
