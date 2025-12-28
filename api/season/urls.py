from django.urls import path, include
from rest_framework.routers import DefaultRouter

from season.views import SeasonViewSet, SeasonRegistrationView, SeasonScoreboardViewSet, CurrentSeasonView, \
    SeasonParticipantViewSet, LiveEventViewSet

router = DefaultRouter()
router.register('seasons', SeasonViewSet, basename='seasons')
router.register('season-scoreboards', SeasonScoreboardViewSet, basename='season-scoreboards')
router.register('season-participants', SeasonParticipantViewSet, basename='season-participants')
router.register('live-events', LiveEventViewSet, basename='live-events')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', SeasonRegistrationView.as_view(), name='season-register'),
    path('current/', CurrentSeasonView.as_view(), name='season-current'),
]
