from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet
from result.views import ResultViewSet, MatchResultViewSet

router = DefaultRouter()

router.register('results', ResultViewSet, basename='results')
router.register('match-results', MatchResultViewSet, basename='match-results')

urlpatterns = [
    path('', include(router.urls)),
]
