from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, MeViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('me', MeViewSet, basename='me')

urlpatterns = [
    path('', include(router.urls)),
]
