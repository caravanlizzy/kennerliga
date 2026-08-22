from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from game.models import Game
from statistic.services import (
    DEFAULT_GAME_MIN_GAMES,
    DEFAULT_MIN_GAMES,
    DEFAULT_POPULAR_GAMES_N,
    DEFAULT_TOP_N,
    DEFAULT_WINDOW,
    get_game_leaderboard,
    get_popular_games,
    get_statistics_overview,
    list_games_with_stats,
    parse_years,
    parse_player_counts,
)


def _int_param(request, name, default):
    raw = request.query_params.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class StatisticsOverviewView(APIView):
    """
    GET /api/statistics/overview/?years=2025,2026&min_games=3&window=2&top_n=5

    Returns, for every key player-ranking category, the requesting player's
    own rank, the players immediately above/below them, and the overall top
    players -- so a player can always see the best players AND exactly
    where they themselves stand.
    """

    def get(self, request):
        profile = request.user.profile
        years = parse_years(request.query_params.get("years"))
        player_counts = parse_player_counts(request.query_params.get("player_count"))
        min_games = max(0, _int_param(request, "min_games", DEFAULT_MIN_GAMES))
        window = max(1, min(5, _int_param(request, "window", DEFAULT_WINDOW)))
        top_n = max(1, min(200, _int_param(request, "top_n", DEFAULT_TOP_N)))

        data = get_statistics_overview(
            profile,
            years=years,
            player_counts=player_counts,
            min_games=min_games,
            window=window,
            top_n=top_n,
        )
        return Response(data)


class GameStatisticsListView(APIView):
    """
    GET /api/statistics/games/?years=2025

    Lists every game with recorded results, most played first, for use as a
    picker feeding the per-game leaderboard below.
    """

    def get(self, request):
        years = parse_years(request.query_params.get("years"))
        player_counts = parse_player_counts(request.query_params.get("player_count"))
        return Response(list_games_with_stats(years=years, player_counts=player_counts))


class PopularGamesView(APIView):
    """
    GET /api/statistics/games/popular/?years=2025&player_count=4p&top_n=3

    Returns the most picked and most banned games (top N each), leading the
    games statistics section before the per-game leaderboard.
    """

    def get(self, request):
        years = parse_years(request.query_params.get("years"))
        player_counts = parse_player_counts(request.query_params.get("player_count"))
        top_n = max(1, min(10, _int_param(request, "top_n", DEFAULT_POPULAR_GAMES_N)))
        return Response(
            get_popular_games(years=years, player_counts=player_counts, top_n=top_n)
        )


class GameLeaderboardView(APIView):
    """
    GET /api/statistics/games/<game_id>/leaderboard/?years=2025&min_games=2

    Ranks every player who has played a specific game, so users can browse
    who performs best at any given game.
    """

    def get(self, request, game_id):
        game = get_object_or_404(Game, pk=game_id)
        profile = request.user.profile
        years = parse_years(request.query_params.get("years"))
        player_counts = parse_player_counts(request.query_params.get("player_count"))
        min_games = max(0, _int_param(request, "min_games", DEFAULT_GAME_MIN_GAMES))

        data = get_game_leaderboard(
            game, profile, years=years, player_counts=player_counts, min_games=min_games
        )
        return Response(data)
