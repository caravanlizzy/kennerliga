from django.urls import path, include
from rest_framework.routers import DefaultRouter

from release_note.views import ReleaseNoteViewSet

router = DefaultRouter()
router.register("release-notes", ReleaseNoteViewSet, basename="release-notes")

urlpatterns = [
    path("", include(router.urls)),
]
