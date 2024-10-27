from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import LeagueViewSet
from result.views import ResultViewSet

router = DefaultRouter()

router.register('results', ResultViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls)),
]
