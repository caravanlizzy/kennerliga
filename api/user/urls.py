from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, MeViewSet, UserRegistrationViewSet, UserInviteLinkViewSet, FeedbackViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('profiles', UserViewSet, basename='profiles')
router.register('me', MeViewSet, basename='me')
router.register('invitations', UserInviteLinkViewSet, basename='invitations')
router.register('register', UserRegistrationViewSet, basename='register')
router.register('feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
