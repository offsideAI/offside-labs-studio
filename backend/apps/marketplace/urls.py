from rest_framework.routers import DefaultRouter

from .views import MarketplaceAgentViewSet

router = DefaultRouter()
router.register(r"marketplace/agents", MarketplaceAgentViewSet, basename="marketplace-agent")

urlpatterns = router.urls
