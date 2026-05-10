from rest_framework.routers import DefaultRouter

from .views import ImportRunViewSet

router = DefaultRouter()
router.register(r"imports", ImportRunViewSet, basename="import-run")

urlpatterns = router.urls
