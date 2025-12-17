# Create your views here.
from collections import defaultdict
from typing import List, Dict

from django.db.models import Prefetch
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from chat.service import create_chat_announcement
from league.models import League, LeagueStanding, GameStanding
from season.queries import register, is_profile_registered, get_open_season
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
        open_season = get_open_season()
        # if not player_profile in current_season.participants.all():
        if not is_profile_registered(player_profile, open_season):
            register(player_profile)
            create_chat_announcement(f"{player_profile.user.username} registered for {open_season.name}")
            return Response(f'Participant {player_profile.profile_name} has been added to the current season.')
        return Response(f'Player {player_profile.profile_name} is already registered')


class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filterset_fields = ['year', 'month', 'status']

    @action(detail=False, methods=['get'], url_path='registration-status')
    def registration_status(self, request):
        """
        Check if the current user is registered in the open season.
        Returns:
        {
          "has_open_season": bool,
          "registered": bool,
          "season_id": int | null
        }
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get the player's profile
        try:
            profile = PlayerProfile.objects.get(user=user)
        except PlayerProfile.DoesNotExist:
            return Response(
                {
                    "has_open_season": False,
                    "registered": False,
                    "season_id": None,
                    "detail": "No PlayerProfile found for this user.",
                },
                status=status.HTTP_200_OK,
            )

        # Get the open season (if any)
        open_season = get_open_season()
        if not open_season:
            return Response(
                {
                    "has_open_season": False,
                    "registered": False,
                    "season_id": None,
                },
                status=status.HTTP_200_OK,
            )

        # Check if the profile is registered in the open season
        registered = is_profile_registered(profile=profile, season=open_season)

        return Response(
            {
                "has_open_season": True,
                "registered": registered,
                "season_id": open_season.id,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="league-winners")
    @action(detail=True, methods=["get"], url_path="league-winners")
    def league_winners(self, request, pk=None):
        """
        GET /seasons/{id}/league-winners/

        Returns the winner (most league_points) for each league in the season.

        Shape:
        {
          "season": {"id": 1, "name": "2025_S10", "status": "RUNNING"},
          "winners": [
            {
              "league": {"id": 10, "level": 1},
              "winner": {"profile_id": 7, "profile_name": "Alice", "username": "alice"},
              "league_points": 42
            },
            ...
          ]
        }
        """
        season = get_object_or_404(
            Season.objects.only("id", "year", "month", "status"),
            pk=pk,
        )

        leagues = (
            League.objects
            .filter(season_id=season.id)
            .order_by("level", "id")
        )

        standings = (
            LeagueStanding.objects
            .filter(league__in=leagues)
            .select_related("league", "player_profile", "player_profile__user")
            .order_by("league_id", "-league_points", "-points", "id")
        )

        winner_by_league_id = {}
        for ls in standings:
            if ls.league_id not in winner_by_league_id:
                winner_by_league_id[ls.league_id] = ls

        winners_payload = []
        for league in leagues:
            ls = winner_by_league_id.get(league.id)
            profile = getattr(ls, "player_profile", None) if ls else None
            user = getattr(profile, "user", None) if profile else None

            winners_payload.append(
                {
                    "league": {"id": league.id, "level": league.level},
                    "winner": (
                        {
                            "profile_id": profile.id,
                            "profile_name": profile.profile_name,
                            "username": getattr(user, "username", None),
                        }
                        if profile
                        else None
                    ),
                    "league_points": getattr(ls, "league_points", None) if ls else None,
                }
            )

        return Response(
            {
                "season": {"id": season.id, "name": season.name, "status": season.status},
                "winners": winners_payload,
            },
            status=status.HTTP_200_OK,
        )


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
        .values('profile', 'profile__profile_name')
    )
    members = list(members_qs)
    player_order: List[int] = [m['profile'] for m in members]
    player_names: Dict[int, str] = {m['profile']: m['profile__profile_name'] for m in members}

    # All per-game standings for this league
    gs_qs = (
        GameStanding.objects
        .filter(league=league.id)
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
        points_by_player = {s.player_profile: getattr(s, 'ingame_points', None) for s in standings}

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
        .filter(league=league.id)
        .select_related('player_profile')
    )
    league_points_by_player = {ls.player_profile: getattr(ls, 'league_points', 0) for ls in ls_qs}

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
    filterset_fields = ["season", "profile__profile_name"]

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """
        GET /season-participants/current/

        Returns all participants of the *current open season*.
        If no open season exists, returns an empty list.
        """
        season = get_open_season()
        if not season:
            # frontend can just treat this as "no participants / no open season"
            return Response([], status=200)

        qs = self.get_queryset().filter(season=season)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)