from rest_framework.routers import DefaultRouter

from .views import CustomFieldDefViewSet

router = DefaultRouter()
router.register(r"custom-field-defs", CustomFieldDefViewSet, basename="custom-field-def")

urlpatterns = router.urls
