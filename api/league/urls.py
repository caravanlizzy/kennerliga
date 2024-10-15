from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet

router = DefaultRouter()

router.register('leagues', LeagueViewSet, basename='leagues')

urlpatterns = [
    path('', include(router.urls)),
]
