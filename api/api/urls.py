from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet
from api.views import LoginApiView
from rest_framework.authtoken import views

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('login/', LoginApiView.as_view()),
    path('', include(router.urls)),
    path('game/', include('game.urls')),
    path('api-token-auth/', views.obtain_auth_token)
]
