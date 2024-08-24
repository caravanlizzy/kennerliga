from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import LoginApiView
from user.views import UserViewSet

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('login/', LoginApiView.as_view()),
    path('', include(router.urls)),
    path('game/', include('game.urls')),
    path('season/', include('season.urls')),
    path('organisation/', include('organisation.urls')),
    path('chat/', include('chat.urls')),
    path('api-token-auth/', views.obtain_auth_token)
]
