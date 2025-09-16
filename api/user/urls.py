from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.models import UserInvitation
from user.views import UserViewSet, MeViewSet, UserInvitationViewSet, UserRegistrationViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('me', MeViewSet, basename='me')
router.register('invitations', UserInvitationViewSet, basename='invitations')
router.register('register', UserRegistrationViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
]
