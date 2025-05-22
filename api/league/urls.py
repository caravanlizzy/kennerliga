from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet, LeagueDetailViewSet  # Make sure NextPlayerView is imported

router = DefaultRouter()
router.register('leagues', LeagueViewSet, basename='leagues')
router.register('league-details', LeagueDetailViewSet, basename='league-details')

urlpatterns = [
    path('', include(router.urls)),
]