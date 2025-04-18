from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet, NextPlayer, LeagueDetailViewSet  # Make sure NextPlayerView is imported

router = DefaultRouter()
router.register('leagues', LeagueViewSet, basename='leagues')
router.register('league-details', LeagueDetailViewSet, basename='league-details')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:league_id>/next-player/', NextPlayer.as_view(), name='next-player'),
]