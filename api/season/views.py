# Create your views here.
from collections import defaultdict
from typing import List, Dict

from django.db.models import Prefetch
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from league.models import League, LeagueStanding, GameStanding
from season.queries import register, is_profile_registered
from season_manager import SeasonManager
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer, SeasonParticipantSerializer
from user.models import PlayerProfile


class SeasonRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        if not self.request.user:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            return HttpResponseNotFound("Player profile not found.")
        current_season = SeasonManager.get_current_season()
        # if not player_profile in current_season.participants.all():
        if not is_profile_registered(player_profile, current_season):
            register(player_profile)
            return Response(f'Participant {player_profile.profile_name} has been added to the current season.')
        return Response(f'Player {player_profile.profile_name} is already registered')


class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


def build_league_scoreboard_payload(league: League) -> dict:
    """
    Compose a grid-friendly scoreboard payload for a single league.

    Shape:
    {
      "league": {"id": ..., "name": ...},
      "columns": ["Game", "Alice", "Bob", ...],
      "rows": [
        {"type":"game","selected_game_id":12,"game":"Catan","cells":[{"player_id":..,"profile_name":"Alice","value":83,"display":"83 pts"}, ...]},
        {"type":"league_totals","label":"League Points","cells":[...]}
      ]
    }
    """
    # Establish player order once (rank, then id)
    members_qs = (
        league.members
        .select_related('profile__user')
        .order_by('rank', 'id')
        .values('profile_id', 'profile__profile_name')
    )
    members = list(members_qs)
    player_order: List[int] = [m['profile_id'] for m in members]
    player_names: Dict[int, str] = {m['profile_id']: m['profile__profile_name'] for m in members}

    # All per-game standings for this league
    gs_qs = (
        GameStanding.objects
        .filter(league_id=league.id)
        .select_related('player_profile', 'selected_game__game')
        .order_by('selected_game_id', 'rank')
    )

    # Group rows by selected_game
    by_game: Dict[int, list] = defaultdict(list)
    game_meta: Dict[int, dict] = {}
    for row in gs_qs:
        by_game[row.selected_game_id].append(row)
        if row.selected_game_id not in game_meta:
            game_meta[row.selected_game_id] = {
                'game_name': getattr(row.selected_game.game, 'name', str(row.selected_game.game))
            }

    # Columns: "Game" + players
    columns = ["Game"] + [player_names.get(pid, f"Player {pid}") for pid in player_order]

    # Build game rows
    rows: List[dict] = []
    for selected_game_id, standings in by_game.items():
        points_by_player = {s.player_profile_id: getattr(s, 'ingame_points', None) for s in standings}

        cells = []
        for pid in player_order:
            val = points_by_player.get(pid)
            cells.append({
                "player_id": pid,
                "profile_name": player_names.get(pid, f"Player {pid}"),
                "value": val,
                "display": (f"{val} pts" if val is not None else "—"),
            })

        rows.append({
            "type": "game",
            "selected_game_id": selected_game_id,
            "game": game_meta[selected_game_id]["game_name"],
            "cells": cells,
        })

    # Final league totals row
    ls_qs = (
        LeagueStanding.objects
        .filter(league_id=league.id)
        .select_related('player_profile')
    )
    league_points_by_player = {ls.player_profile_id: getattr(ls, 'league_points', 0) for ls in ls_qs}

    total_cells = []
    for pid in player_order:
        val = league_points_by_player.get(pid, 0)
        total_cells.append({
            "player_id": pid,
            "profile_name": player_names.get(pid, f"Player {pid}"),
            "value": val,
            "display": f"{val} pts",
        })

    rows.append({
        "type": "league_totals",
        "label": "League Points",
        "cells": total_cells,
    })

    return {
        "league": {"id": league.id, "name": league.level},
        "columns": columns,
        "rows": rows,
    }


class SeasonScoreboardViewSet(ViewSet):
    """
    GET /season-scoreboards/{season_id}/scoreboards/
    Returns scoreboards for every league in the season.
    """

    @action(detail=True, methods=['get'], url_path='scoreboards')
    def scoreboards(self, request, pk=None):
        # Load fields needed for 'name' property (year, month) to avoid extra queries
        season = get_object_or_404(
            Season.objects.only('id', 'year', 'month', 'status'),
            pk=pk
        )

        # Fetch leagues for this season (Level 1 = highest)
        leagues = (
            League.objects
            .filter(season_id=season.id)
            .select_related('season')
            .prefetch_related(
                Prefetch(
                    'members',
                    queryset=(
                        League._meta.get_field('members').remote_field.model.objects
                        .select_related('profile__user')
                        .order_by('rank', 'id')
                    )
                )
            )
            .order_by('level', 'id')
        )

        payloads = [build_league_scoreboard_payload(league) for league in leagues]

        return Response(
            {
                "season": {"id": season.id, "name": season.name, "status": season.status},
                "leagues": payloads,
            },
            status=status.HTTP_200_OK
        )


class CurrentSeasonView(APIView):
    """
    GET /season/current/
    Returns the Season for the current year and month.
    Example: { "id": 5, "name": "2025_S10", "status": "RUNNING" }
    """

    def get(self, request):
        today = timezone.localdate()
        year, month = today.year, today.month

        season = Season.objects.filter(year=year, month=month).first()

        if not season:
            return Response(
                {"detail": f"No season found for {year}-{month}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"id": season.id, "name": season.name, "status": season.status},
            status=status.HTTP_200_OK,
        )

class SeasonParticipantViewSet(ModelViewSet):
    """
    list:   GET  /season-participants/?season=<id>
    create: POST /season-participants/  {season, profile, rank?}
    """
    queryset = SeasonParticipant.objects.select_related("season", "profile")
    serializer_class = SeasonParticipantSerializer
    permission_classes = [IsAdminUser]  # adjust if needed
    filterset_fields = ["season", "profile"]