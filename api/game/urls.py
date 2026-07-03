# game/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from game.views import (
    GameViewSet,
    GameOptionViewSet,
    GameOptionChoiceViewSet,
    FactionViewSet,
    TieBreakerViewSet,
    ResultConfigViewSet,
    StartingPointSystemViewSet,
    PlatformViewSet,
    SelectedGameViewSet,
    SelectedOptionViewSet,
    FullGameViewSet,
    BanDecisionViewSet,
    WinConditionViewSet,
    WinConditionOptionViewSet,
)

router = DefaultRouter()
router.register("games", GameViewSet, basename="games")
router.register("games-full", FullGameViewSet, basename="full-game")
router.register("options", GameOptionViewSet, basename="game-options")
router.register(
    "option-choices", GameOptionChoiceViewSet, basename="game-option-choices"
)
router.register("factions", FactionViewSet, basename="factions")
router.register("tie-breakers", TieBreakerViewSet, basename="tie-breakers")
router.register("win-conditions", WinConditionViewSet, basename="win-conditions")
router.register(
    "win-condition-options",
    WinConditionOptionViewSet,
    basename="win-condition-options",
)
router.register("result-configs", ResultConfigViewSet, basename="result-configs")
router.register(
    "starting-point-systems",
    StartingPointSystemViewSet,
    basename="starting-point-systems",
)
router.register("platforms", PlatformViewSet, basename="platforms")
router.register("selected-games", SelectedGameViewSet, basename="selected-games")
router.register(
    "selected-game-options", SelectedOptionViewSet, basename="selected-game-options"
)
router.register("ban-decisions", BanDecisionViewSet, basename="ban-decisions")

urlpatterns = [
    path("", include(router.urls)),
]
