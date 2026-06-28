# Create your views here.
from collections import defaultdict
from typing import Dict

from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding, GameStanding
from result.models import Result
from season.queries import (
    register,
    is_profile_registered,
    get_open_season,
    get_running_season,
)
from season.models import Season, SeasonParticipant
from season.scoreboard_payload import build_season_scoreboards
from league.services import build_full_standings_for_season
from season.serializer import (
    SeasonSerializer,
    SeasonParticipantSerializer,
    TLiveEventSerializer,
    SeasonWithLeaguesSerializer,
)
from user.models import PlayerProfile


class SeasonRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        if not self.request.user:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            return HttpResponseNotFound("Player profile not found.")
        open_season = get_open_season()
        # if not player_profile in current_season.participants.all():
        if not is_profile_registered(player_profile, open_season):
            register(player_profile)
            return Response(
                f"Participant {player_profile.profile_name} has been added to the current season."
            )
        return Response(f"Player {player_profile.profile_name} is already registered")


class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all().order_by("-year", "-month")
    serializer_class = SeasonSerializer
    filterset_fields = ["year", "month", "status"]

    def get_serializer_class(self):
        if (
            self.action == "list"
            and self.request.query_params.get("include_details") == "1"
        ):
            return SeasonWithLeaguesSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("with_leagues") == "1":
            return qs.filter(leagues__isnull=False).distinct()
        return qs

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "registration_status",
            "league_winners",
            "seasons_with_leagues",
            "full_standings",
        ]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=True, methods=["get"], url_path="full-standings")
    def full_standings(self, request, pk=None):
        """
        GET /seasons/{id}/full-standings/

        Batched endpoint that returns full-standings payloads for every league
        in the season in a single response. Replaces the previous frontend
        pattern of issuing 1 + N HTTP calls (one for the league list and one
        per league for its full standings) and keeps the SQL count constant
        regardless of league count.
        """
        season = get_object_or_404(
            Season.objects.only("id", "year", "month", "status"), pk=pk
        )
        leagues = list(
            League.objects.filter(season_id=season.id)
            .select_related("season")
            .order_by("level", "id")
        )
        payloads = build_full_standings_for_season(leagues)
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

    @action(detail=False, methods=["get"], url_path="seasons-with-leagues")
    def seasons_with_leagues(self, request):
        queryset = self.get_queryset().filter(leagues__isnull=False).distinct()
        serializer = SeasonWithLeaguesSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="registration-status")
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

        leagues = League.objects.filter(season_id=season.id).order_by("level", "id")

        standings = (
            LeagueStanding.objects.filter(league__in=leagues)
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
                "season": {
                    "id": season.id,
                    "name": season.name,
                    "status": season.status,
                },
                "winners": winners_payload,
            },
            status=status.HTTP_200_OK,
        )


class SeasonScoreboardViewSet(ViewSet):
    """
    GET /season-scoreboards/{season_id}/scoreboards/
    Returns scoreboards for every league in the season.
    """

    @action(detail=True, methods=["get"], url_path="scoreboards")
    def scoreboards(self, request, pk=None):
        # Load fields needed for 'name' property (year, month) to avoid extra queries
        season = get_object_or_404(
            Season.objects.only("id", "year", "month", "status"), pk=pk
        )

        # Fetch leagues for this season (Level 1 = highest). Members are
        # prefetched once and reused by the scoreboard payload builder, which
        # also bulk-loads GameStanding/LeagueStanding for the whole season.
        leagues = list(
            League.objects.filter(season_id=season.id)
            .select_related("season")
            .prefetch_related(
                Prefetch(
                    "members",
                    queryset=(
                        SeasonParticipant.objects.select_related("profile__user")
                        .order_by("rank", "id")
                    ),
                )
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

    def _previous_season_for(self, season: Season):
        if not season:
            return None
        # Try exact previous month
        prev_year = season.year
        prev_month = season.month - 1
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        prev = Season.objects.filter(year=prev_year, month=prev_month).first()
        if prev:
            return prev
        # Fallback: any earlier season
        return (
            Season.objects.filter(
                (Q(year__lt=season.year))
                | (Q(year=season.year) & Q(month__lt=season.month))
            )
            .order_by("-year", "-month")
            .first()
        )

    def _augment_with_prev_unregistered(self, season: Season, data_list: list):
        """Append entries for profiles from the previous season who are not in the given season."""
        if not season:
            return data_list
        prev = self._previous_season_for(season)
        if not prev:
            return data_list

        # Current registered profiles
        current_profiles = set(
            SeasonParticipant.objects.filter(season=season).values_list(
                "profile_id", flat=True
            )
        )
        # Previous season profiles
        prev_profiles = list(
            SeasonParticipant.objects.filter(season=prev).values_list(
                "profile_id", flat=True
            )
        )

        missing_ids = [pid for pid in prev_profiles if pid not in current_profiles]
        if not missing_ids:
            return data_list

        # Load profiles with related user for names
        profiles = PlayerProfile.objects.select_related("user").filter(
            id__in=missing_ids
        )
        # Prepare season details once
        season_details = SeasonSerializer(season).data

        for p in profiles:
            data_list.append(
                {
                    "id": None,
                    "season": season.id,
                    "profile": p.id,
                    "rank": None,
                    "username": getattr(getattr(p, "user", None), "username", None),
                    "profile_name": p.profile_name,
                    "season_details": season_details,
                    "selected_games": [],
                    "has_banned": False,
                    "is_active_player": False,
                    "is_prev_unregistered": True,
                    "my_banned_game": None,
                }
            )
        return data_list

    def list(self, request, *args, **kwargs):
        # Use default list to get current registered entries, then augment if season provided
        season_id = request.query_params.get("season")
        # Opt-in flag: only include previous unregistered players when explicitly requested
        include_prev_unregistered = str(
            request.query_params.get("include_prev_unregistered", "")
        ).lower() in ("1", "true", "yes", "y", "t")
        response = super().list(request, *args, **kwargs)
        if not season_id:
            return response
        try:
            season = Season.objects.get(pk=season_id)
        except Season.DoesNotExist:
            return response

        if include_prev_unregistered:
            data = list(response.data)
            data = self._augment_with_prev_unregistered(season, data)
            return Response(data)
        # Default behaviour: return only registered participants
        return response

    @action(detail=False, methods=["get"], url_path="projected-leagues")
    def projected_leagues(self, request):
        """
        GET /season-participants/projected-leagues/?season=<id>

        For an upcoming/open season, project how the currently-registered
        participants would be distributed across leagues for that season,
        applying the same promotion/relegation logic used when ranks are
        finalized (see ``season.services.apply_promotion``).

        Participants with a finalized result from the previous season are
        placed into their projected league. Newcomers (no previous-season
        result available) are returned in a ``shuffle_pool`` since their
        final league depends on the random shuffle performed at season
        start.

        Response:
        {
          "season": {"id", "name", "status"},
          "leagues": [{"level": 1, "size": 4, "members": [
              {"profile": .., "profile_name": .., "username": ..,
               "prev_league": .., "prev_position": ..}
          ]}, ...],
          "shuffle_pool": [
              {"profile": .., "profile_name": .., "username": ..}
          ]
        }
        """
        from season.services import (
            _players_per_league,
            apply_promotion,
            get_previous_result,
        )

        season_id = request.query_params.get("season")
        season = None
        if season_id:
            try:
                season = Season.objects.get(pk=season_id)
            except Season.DoesNotExist:
                season = None
        if not season:
            season = get_open_season()
        if not season:
            season = get_running_season()
        if not season:
            return Response(
                {"season": None, "leagues": [], "shuffle_pool": []}, status=200
            )

        participants = list(
            SeasonParticipant.objects.filter(season=season).select_related(
                "profile", "profile__user"
            )
        )
        total = len(participants)
        sizes = _players_per_league(total) if total else []

        prev_rows = []
        newcomers = []
        for sp in participants:
            info = get_previous_result(sp.profile)
            base = {
                "profile": sp.profile_id,
                "profile_name": sp.profile.profile_name,
                "username": getattr(
                    getattr(sp.profile, "user", None), "username", None
                ),
            }
            if info and info.get("position") is not None:
                prev_rows.append(
                    {
                        **base,
                        "league": info["league"],
                        "position": info["position"],
                        "is_last": info["is_last"],
                    }
                )
            else:
                newcomers.append(base)

        ordered = apply_promotion(prev_rows, sizes if sizes else None)

        # Distribute ordered prev participants into leagues by capacity.
        leagues_payload = []
        idx = 0
        for level, size in enumerate(sizes, start=1):
            chunk = ordered[idx : idx + size]
            idx += size
            members = [
                {
                    "profile": r["profile"],
                    "profile_name": r["profile_name"],
                    "username": r["username"],
                    "prev_league": r.get("league"),
                    "prev_position": r.get("position"),
                }
                for r in chunk
            ]
            leagues_payload.append(
                {"level": level, "size": size, "members": members}
            )

        return Response(
            {
                "season": {
                    "id": season.id,
                    "name": season.name,
                    "status": season.status,
                },
                "leagues": leagues_payload,
                "shuffle_pool": newcomers,
            },
            status=200,
        )

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """
        GET /season-participants/current/

        Returns all participants of the current running or open season, and also
        includes players who participated in the previous season but have not yet
        registered in the current one.
        If no such season exists, returns an empty list.
        """
        include_prev_unregistered = str(
            request.query_params.get("include_prev_unregistered", "")
        ).lower() in ("1", "true", "yes", "y", "t")
        season = get_running_season()
        if not season:
            season = get_open_season()

        if not season:
            return Response([], status=200)

        qs = self.get_queryset().filter(season=season)
        serializer = self.get_serializer(qs, many=True)
        if include_prev_unregistered:
            data = list(serializer.data)
            data = self._augment_with_prev_unregistered(season, data)
            return Response(data)
        # Default behaviour: return only registered participants
        return Response(serializer.data)


class LiveEventViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        season_id = request.query_params.get("season_id")
        if not season_id:
            season = get_running_season()
            if not season:
                season = get_open_season()
            if not season:
                # Fallback to most recent season
                season = Season.objects.order_by("-year", "-month").first()
            if not season:
                return Response([])
            season_id = season.id

        # Annotate member_count once instead of running .count() per league.
        leagues = list(
            League.objects.filter(season_id=season_id).annotate(
                member_count=Count("members")
            )
        )
        events = []

        # 1. PICK events
        picks = SelectedGame.objects.filter(league__in=leagues).select_related(
            "profile", "game", "league"
        )
        for pick in picks:
            events.append(
                {
                    "id": f"pick-{pick.id}",
                    "type": "PICK",
                    "timestamp": pick.created_at,
                    "leagueLevel": pick.league.level,
                    "leagueId": pick.league.id,
                    "data": {
                        "playerName": pick.profile.profile_name,
                        "gameName": pick.game.name,
                    },
                }
            )

        # 2. BAN events
        bans = BanDecision.objects.filter(
            Q(league__in=leagues)
            & (Q(skipped_ban=True) | Q(selected_game__isnull=False))
        ).select_related("player_banning", "selected_game__game", "league")
        for ban in bans:
            game_name = ban.selected_game.game.name if ban.selected_game else None
            events.append(
                {
                    "id": f"ban-{ban.id}",
                    "type": "BAN",
                    "timestamp": ban.created_at,
                    "leagueLevel": ban.league.level,
                    "leagueId": ban.league.id,
                    "data": {
                        "playerName": ban.player_banning.profile_name,
                        "gameName": game_name,
                        "skippedBan": ban.skipped_ban,
                    },
                }
            )

        # 3. LEAGUE_RUNNING events (picking/banning done; games actually played)
        # Emitted once a league has moved past the pick/ban phase.
        running_statuses = {"PLAYING", "DONE"}
        # Group picks per league
        picks_by_league: Dict[int, list] = defaultdict(list)
        for pick in picks:
            picks_by_league[pick.league_id].append(pick)
        # Group bans per league
        bans_by_league: Dict[int, list] = defaultdict(list)
        for ban in bans:
            bans_by_league[ban.league_id].append(ban)

        for league in leagues:
            if league.status not in running_statuses:
                continue
            league_picks = picks_by_league.get(league.id, [])
            if not league_picks:
                continue
            # A game is successfully banned only if the number of BanDecisions
            # targeting it reaches the league's min_bans threshold
            # (2 for leagues with > 2 members, else 1). Picks with fewer bans
            # are still being played.
            member_count = league.member_count or 0
            min_bans = 2 if member_count > 2 else 1
            ban_counts_by_sg: Dict[int, int] = defaultdict(int)
            for b in bans_by_league.get(league.id, []):
                if b.selected_game_id is not None:
                    ban_counts_by_sg[b.selected_game_id] += 1
            banned_sg_ids = {
                sg_id
                for sg_id, c in ban_counts_by_sg.items()
                if c >= min_bans
            }
            playing_picks = [p for p in league_picks if p.id not in banned_sg_ids]
            if not playing_picks:
                continue

            league_bans = bans_by_league.get(league.id, [])
            # Ensure the LEAGUE_RUNNING event always appears strictly after
            # every PICK and BAN of that league on the timeline. We therefore
            # take the latest timestamp across both picks and bans, using
            # `updated_at` as well as `created_at` so that picks which were
            # re-saved (e.g. repicks replacing a banned game on the same row)
            # are also taken into account.
            candidate_times = []
            for p in league_picks:
                candidate_times.append(p.created_at)
                if getattr(p, "updated_at", None):
                    candidate_times.append(p.updated_at)
            for b in league_bans:
                candidate_times.append(b.created_at)
            event_time = max(candidate_times)

            games_payload = [
                {
                    "playerName": p.profile.profile_name,
                    "gameName": p.game.name,
                }
                for p in playing_picks
            ]

            events.append(
                {
                    "id": f"league-running-{league.id}",
                    "type": "LEAGUE_RUNNING",
                    "timestamp": event_time,
                    "leagueLevel": league.level,
                    "leagueId": league.id,
                    "data": {
                        "leagueLevel": league.level,
                        "games": games_payload,
                    },
                }
            )

        # 4. GAME_FINISHED events
        # Get all results for these leagues
        results = Result.objects.filter(league__in=leagues).select_related(
            "player_profile", "selected_game__game", "league"
        )
        # Group results by selected_game
        results_by_game = defaultdict(list)
        for r in results:
            results_by_game[r.selected_game_id].append(r)

        # Member counts come from the annotation above (single query).
        league_member_counts = {l.id: l.member_count for l in leagues}

        # Bulk-load all LeagueStanding rows for the season once and group
        # by league_id in Python; replaces per-league queries below.
        standings_by_league: Dict[int, list] = defaultdict(list)
        for ls in (
            LeagueStanding.objects.filter(
                league_id__in=[l.id for l in leagues]
            )
            .select_related("player_profile")
            .order_by("-league_points", "-wins")
        ):
            standings_by_league[ls.league_id].append(ls)

        for sg_id, res_list in results_by_game.items():
            if not res_list:
                continue
            league_id = res_list[0].league_id
            member_count = league_member_counts.get(league_id, 0)
            if len(res_list) == member_count and member_count > 0:
                # Game is finished.
                # The timestamp should be the time of the LAST result.
                last_result_time = max(r.created_at for r in res_list)

                # Prepare full results list. Use finalized MatchResults (Result.position) as the base.
                # Keep a stable secondary order by player name only for display purposes.
                full_results = sorted(
                    res_list,
                    key=lambda r: (
                        r.position is None,
                        r.position if r.position is not None else 10**9,
                        (r.player_profile.profile_name or ""),
                    ),
                )

                # Determine winners respecting ties: all players with the best (lowest) position.
                # This leverages MatchResult finalization which already applied tie-breakers; remaining equal
                # positions represent a genuine tie.
                min_pos = None
                winners = []
                for r in full_results:
                    if r.position is None:
                        continue
                    if min_pos is None:
                        min_pos = r.position
                    if r.position == min_pos:
                        winners.append(r)
                    else:
                        break

                # Backward compatibility: expose both 'winners' (array) and a legacy 'winner' string.
                # 'winner' will now reflect all winners joined by comma to avoid implying a single victor.
                primary_winner = (
                    winners[0]
                    if winners
                    else (full_results[0] if full_results else None)
                )
                winners_names = (
                    [w.player_profile.profile_name for w in winners]
                    if winners
                    else (
                        []
                        if primary_winner is None
                        else [primary_winner.player_profile.profile_name]
                    )
                )
                results_payload = [
                    {
                        "playerName": r.player_profile.profile_name,
                        "position": r.position,
                        "points": r.points,
                    }
                    for r in full_results
                ]

                events.append(
                    {
                        "id": f"finish-{sg_id}",
                        "type": "GAME_FINISHED",
                        "timestamp": last_result_time,
                        "leagueLevel": res_list[0].league.level,
                        "leagueId": league_id,
                        "data": {
                            "gameName": res_list[0].selected_game.game.name,
                            "winner": ", ".join(winners_names)
                            if winners_names
                            else None,
                            "winners": winners_names,
                            "points": primary_winner.points if primary_winner else None,
                            "results": results_payload,
                        },
                    }
                )

        # 4. LEAGUE_FINISHED events
        for league in leagues:
            if not league.is_finished:
                continue

            standings = standings_by_league.get(league.id, [])
            if standings:
                top_standing = standings[0]
                # Get all players tied for first place
                winners = [
                    s.player_profile.profile_name
                    for s in standings
                    if s.league_points == top_standing.league_points
                    and s.wins == top_standing.wins
                ]
            else:
                winners = []

            events.append(
                {
                    "id": f"league-done-{league.id}",
                    "type": "LEAGUE_FINISHED",
                    "timestamp": league.updated_at,
                    "leagueLevel": league.level,
                    "leagueId": league.id,
                    "data": {"leagueLevel": league.level, "winners": winners},
                }
            )

        # 5. SEASON_FINISHED events
        season = Season.objects.filter(id=season_id).first()
        if season and season.status == Season.SeasonStatus.DONE:
            # Find winner of Level 1 league (reuse the bulk standings load)
            l1 = next((l for l in leagues if l.level == 1), None)
            winner_name = "Unknown"
            if l1:
                l1_standings = standings_by_league.get(l1.id, [])
                if l1_standings:
                    winner_name = l1_standings[0].player_profile.profile_name

            events.append(
                {
                    "id": f"season-done-{season.id}",
                    "type": "SEASON_FINISHED",
                    "timestamp": season.updated_at,
                    "leagueId": None,
                    "data": {
                        "seasonName": f"{season.year}-{season.month:02d}",
                        "seasonWinner": winner_name,
                    },
                }
            )

        # Sort
        # Secondary key: when timestamps tie, ensure LEAGUE_RUNNING summaries
        # come AFTER the PICK/BAN events that led to them (and BEFORE later
        # events such as GAME_FINISHED). With reverse=True (newest first), a
        # higher secondary value appears earlier in the rendered list, so
        # LEAGUE_RUNNING gets a higher rank than PICK/BAN on ties.
        type_order = {
            "PICK": 0,
            "BAN": 0,
            "LEAGUE_RUNNING": 1,
            "GAME_FINISHED": 2,
            "LEAGUE_FINISHED": 3,
            "SEASON_FINISHED": 4,
        }
        events.sort(
            key=lambda x: (x["timestamp"], type_order.get(x["type"], 0)),
            reverse=True,
        )
        limit = request.query_params.get("limit")
        if limit:
            try:
                limit = int(limit)
                events = events[:limit]
            except ValueError:
                pass

        serializer = TLiveEventSerializer(events, many=True)
        return Response(serializer.data)
