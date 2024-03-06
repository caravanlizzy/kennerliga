from django.urls import path, include
from rest_framework import routers
from game.views import GameViewSet, GameOptionViewSet, GameOptionChoiceViewSet
from user.views import UserViewSet
from api.views import LoginApiView
from rest_framework.authtoken import views

router = routers.SimpleRouter()

router.register('games', GameViewSet, basename='games')
router.register('game-options', GameOptionViewSet, basename='game-options')
router.register('game-options', GameOptionChoiceViewSet, basename='game-option-choices')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('login/', LoginApiView.as_view()),
    path('', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token)
]
