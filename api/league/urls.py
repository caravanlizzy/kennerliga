from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet, SelectGameView  # Make sure NextPlayerView is imported

router = DefaultRouter()
router.register('leagues', LeagueViewSet, basename='leagues')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:league_id>/next-player/', SelectGameView.as_view(), name='next-player'),
]