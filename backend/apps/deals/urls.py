from rest_framework.routers import DefaultRouter

from .views import DealViewSet, PipelineViewSet

router = DefaultRouter()
router.register(r"pipelines", PipelineViewSet, basename="pipeline")
router.register(r"deals", DealViewSet, basename="deal")

urlpatterns = router.urls
