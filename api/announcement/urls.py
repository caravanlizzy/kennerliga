from django.urls import path, include
from rest_framework.routers import DefaultRouter

from announcement.views import AnnouncementViewSet

router = DefaultRouter()
router.register('announcements', AnnouncementViewSet, basename='announcements')

urlpatterns = [
    path('', include(router.urls)),
]
