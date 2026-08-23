from django.urls import path, include
from rest_framework.routers import DefaultRouter

from configuration.views import AppConfigurationViewSet

router = DefaultRouter()
router.register(
    "app-configurations", AppConfigurationViewSet, basename="app-configurations"
)

urlpatterns = [
    path("", include(router.urls)),
]
