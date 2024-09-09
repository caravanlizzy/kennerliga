from django.urls import path, include
from rest_framework.routers import DefaultRouter

from season.views import SeasonViewSet, SeasonRegistrationView

router = DefaultRouter()

router.register('seasons', SeasonViewSet, basename='season')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', SeasonRegistrationView.as_view()),
]
