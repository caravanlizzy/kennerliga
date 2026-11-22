from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from game.models import SelectedGame
from league.models import League, LeagueStanding
from result.models import Result
from season.models import Season
from season.scoreboard_payload import build_season_scoreboards


class SeasonScoreboardViewSet(ViewSet):
    """
    API viewset for retrieving scoreboards for all leagues in a specific season.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="scoreboards")
    def scoreboards(self, request, pk=None):
        season = get_object_or_404(
            Season.objects.only("id", "year", "month", "status"), pk=pk
        )

        selected_games_prefetch = Prefetch(
            "selected_games",
            queryset=SelectedGame.objects.select_related("game", "profile").order_by(
                "game__name", "id"
            ),
        )
        standings_prefetch = Prefetch(
            "standings",
            queryset=LeagueStanding.objects.select_related(
                "player_profile__user"
            ).order_by("-league_points", "id"),
        )
        results_prefetch = Prefetch(
            "results",
            queryset=Result.objects.select_related(
                "player_profile",
                "faction",
                "win_condition",
                "selected_game",
                "selected_game__game",
            ).order_by("selected_game_id", "position", "id"),
        )

        leagues = (
            League.objects.filter(season_id=season.id)
            .select_related("season")
            .prefetch_related(
                "members__user",
                selected_games_prefetch,
                standings_prefetch,
                results_prefetch,
            )
            .order_by("level", "id")
        )

        payloads = build_season_scoreboards(leagues)

        return Response(
            {
                "season": {
                    "id": season.id,
                    "name": season.name,
                    "status": season.status,
                },
                "leagues": payloads,
            },
            status=status.HTTP_200_OK,
        )
