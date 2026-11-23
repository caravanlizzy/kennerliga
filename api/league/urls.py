from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import (
    LeagueViewSet,
    LeagueDetailViewSet,
    LeagueTieResolutionViewSet,
)  # Make sure NextPlayerView is imported

router = DefaultRouter()
router.register("leagues", LeagueViewSet, basename="leagues")
router.register("league-details", LeagueDetailViewSet, basename="league-details")
router.register("tie-resolutions", LeagueTieResolutionViewSet, basename="tie-resolutions")

urlpatterns = [
    path("", include(router.urls)),
]
