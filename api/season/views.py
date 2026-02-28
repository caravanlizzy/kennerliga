# Create your views here.
from collections import defaultdict
from typing import List, Dict

from django.db import models
from django.db.models import Prefetch, Q
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
from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding, GameStanding, LeagueStatus
from result.models import Result
from season.queries import register, is_profile_registered, get_open_season, get_running_season
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer, SeasonParticipantSerializer, TLiveEventSerializer, SeasonWithLeaguesSerializer
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
            return Response(f'Participant {player_profile.profile_name} has been added to the current season.')
        return Response(f'Player {player_profile.profile_name} is already registered')


class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all().order_by('-year', '-month')
    serializer_class = SeasonSerializer
    filterset_fields = ['year', 'month', 'status']

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('include_details') == '1':
            return SeasonWithLeaguesSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('with_leagues') == '1':
            return qs.filter(leagues__isnull=False).distinct()
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'registration_status', 'league_winners', 'seasons_with_leagues']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'], url_path='seasons-with-leagues')
    def seasons_with_leagues(self, request):
        queryset = self.get_queryset().filter(leagues__isnull=False).distinct()
        serializer = SeasonWithLeaguesSerializer(queryset, many=True)
        return Response(serializer.data)

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
            .order_by("league_id", "-league_points", "-wins", "id")
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
        season = get_running_season()
        if not season:
            season = get_open_season()

        if not season:
            today = timezone.localdate()
            year, month = today.year, today.month
            season = Season.objects.filter(year=year, month=month).first()

        if not season:
            return Response(
                {"detail": "No active or current month season found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"id": season.id, "name": season.name, "status": season.status},
            status=status.HTTP_200_OK,
        )

class SeasonParticipantViewSet(ModelViewSet):
    """
    list:   GET  /season-participants/?season=<id>&profile=<id>
    create: POST /season-participants/  {season, profile, rank?}
    """
    queryset = SeasonParticipant.objects.select_related("season", "profile")
    serializer_class = SeasonParticipantSerializer
    filterset_fields = ["season", "profile", "profile__profile_name"]

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """
        GET /season-participants/current/

        Returns all participants of the current running or open season.
        If no such season exists, returns an empty list.
        """
        season = get_running_season()
        if not season:
            season = get_open_season()

        if not season:
            # frontend can just treat this as "no participants / no open season"
            return Response([], status=200)

        qs = self.get_queryset().filter(season=season)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class LiveEventViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        season_id = request.query_params.get('season_id')
        if not season_id:
            season = get_running_season()
            if not season:
                season = get_open_season()
            if not season:
                # Fallback to most recent season
                season = Season.objects.order_by('-year', '-month').first()
            if not season:
                return Response([])
            season_id = season.id

        leagues = League.objects.filter(season_id=season_id)
        events = []

        # 1. PICK events
        picks = SelectedGame.objects.filter(league__in=leagues).select_related('profile', 'game', 'league')
        for pick in picks:
            events.append({
                'id': f'pick-{pick.id}',
                'type': 'PICK',
                'timestamp': pick.created_at,
                'leagueLevel': pick.league.level,
                'leagueId': pick.league.id,
                'data': {
                    'playerName': pick.profile.profile_name,
                    'gameName': pick.game.name
                }
            })

        # 2. BAN events
        bans = BanDecision.objects.filter(
            Q(league__in=leagues) & 
            (Q(skipped_ban=True) | Q(selected_game__isnull=False))
        ).select_related('player_banning', 'selected_game__game', 'league')
        for ban in bans:
            game_name = ban.selected_game.game.name if ban.selected_game else None
            events.append({
                'id': f'ban-{ban.id}',
                'type': 'BAN',
                'timestamp': ban.created_at,
                'leagueLevel': ban.league.level,
                'leagueId': ban.league.id,
                'data': {
                    'playerName': ban.player_banning.profile_name,
                    'gameName': game_name,
                    'skippedBan': ban.skipped_ban
                }
            })

        # 3. GAME_FINISHED events
        # Get all results for these leagues
        results = Result.objects.filter(league__in=leagues).select_related('player_profile', 'selected_game__game', 'league')
        # Group results by selected_game
        results_by_game = defaultdict(list)
        for r in results:
            results_by_game[r.selected_game_id].append(r)

        # We need member counts for each league to determine if a game is finished.
        # Let's count members per league.
        league_member_counts = {l.id: l.members.count() for l in leagues}

        for sg_id, res_list in results_by_game.items():
            if not res_list:
                continue
            league_id = res_list[0].league_id
            member_count = league_member_counts.get(league_id, 0)
            if len(res_list) == member_count and member_count > 0:
                # Game is finished.
                # The timestamp should be the time of the LAST result.
                last_result_time = max(r.created_at for r in res_list)

                # Prepare full results list with positions and points
                full_results = sorted(
                    res_list,
                    key=lambda r: (
                        r.position is None,
                        r.position if r.position is not None else -((r.points if r.points is not None else -10**9))
                    )
                )
                # Winner is the first item in the fully sorted results (robust when points or position are missing)
                winner = full_results[0]
                results_payload = [
                    {
                        'playerName': r.player_profile.profile_name,
                        'position': r.position,
                        'points': r.points,
                    }
                    for r in full_results
                ]

                events.append({
                    'id': f'finish-{sg_id}',
                    'type': 'GAME_FINISHED',
                    'timestamp': last_result_time,
                    'leagueLevel': res_list[0].league.level,
                    'leagueId': league_id,
                    'data': {
                        'gameName': res_list[0].selected_game.game.name,
                        'winner': winner.player_profile.profile_name,
                        'points': winner.points,
                        'results': results_payload,
                    }
                })

        # 4. LEAGUE_FINISHED events
        for league in leagues:
            if not league.is_finished:
                continue

            standings = LeagueStanding.objects.filter(league=league).order_by('-league_points', '-wins')
            if standings.exists():
                top_standing = standings.first()
                # Get all players tied for first place
                winners = [
                    s.player_profile.profile_name 
                    for s in standings 
                    if s.league_points == top_standing.league_points and s.wins == top_standing.wins
                ]
            else:
                winners = []

            events.append({
                'id': f'league-done-{league.id}',
                'type': 'LEAGUE_FINISHED',
                'timestamp': league.updated_at,
                'leagueLevel': league.level,
                'leagueId': league.id,
                'data': {
                    'leagueLevel': league.level,
                    'winners': winners
                }
            })

        # 5. SEASON_FINISHED events
        season = Season.objects.filter(id=season_id).first()
        if season and season.status == Season.SeasonStatus.DONE:
            # Find winner of Level 1 league
            l1 = leagues.filter(level=1).first()
            winner_name = "Unknown"
            if l1:
                top_standing = LeagueStanding.objects.filter(league=l1).order_by('-league_points', '-wins').first()
                if top_standing:
                    winner_name = top_standing.player_profile.profile_name

            events.append({
                'id': f'season-done-{season.id}',
                'type': 'SEASON_FINISHED',
                'timestamp': season.updated_at,
                'leagueId': None,
                'data': {
                    'seasonName': f"{season.year}-{season.month:02d}",
                    'seasonWinner': winner_name
                }
            })

        # Sort
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        limit = request.query_params.get('limit')
        if limit:
            try:
                limit = int(limit)
                events = events[:limit]
            except ValueError:
                pass

        serializer = TLiveEventSerializer(events, many=True)
        return Response(serializer.data)
