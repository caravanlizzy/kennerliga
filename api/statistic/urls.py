from django.urls import path

from statistic.views import (
    GameDetailStatisticsView,
    GameLeaderboardView,
    GameStatisticsListView,
    PopularGamesView,
    StatisticsOverviewView,
    WinSuggestionsView,
)

urlpatterns = [
    path("overview/", StatisticsOverviewView.as_view(), name="statistics-overview"),
    path("games/", GameStatisticsListView.as_view(), name="statistics-games"),
    path("games/popular/", PopularGamesView.as_view(), name="statistics-popular-games"),
    path(
        "games/<int:game_id>/",
        GameDetailStatisticsView.as_view(),
        name="statistics-game-detail",
    ),
    path(
        "games/<int:game_id>/details/",
        GameDetailStatisticsView.as_view(),
        name="statistics-game-details",
    ),
    path(
        "games/<int:game_id>/leaderboard/",
        GameLeaderboardView.as_view(),
        name="statistics-game-leaderboard",
    ),
    path(
        "leagues/<int:league_id>/win-suggestions/",
        WinSuggestionsView.as_view(),
        name="statistics-win-suggestions",
    ),
]
