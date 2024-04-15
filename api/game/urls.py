# game/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from game.views import GameViewSet, GameOptionViewSet, GameOptionChoiceViewSet, FactionViewSet, TieBreakerViewSet

router = DefaultRouter()
router.register('games', GameViewSet, basename='games')
router.register('options', GameOptionViewSet, basename='game-options')
router.register('option-choices', GameOptionChoiceViewSet, basename='game-option-choices')
router.register('factions', FactionViewSet, basename='factions')
router.register('tie-breakers', TieBreakerViewSet, basename='tie-breakers')

urlpatterns = [
    path('', include(router.urls)),
]




