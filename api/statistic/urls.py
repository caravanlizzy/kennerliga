from django.urls import path

from statistic.views import (
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
