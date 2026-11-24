from django.db import transaction
from django.http import HttpResponseNotFound
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from league.models import League, LeagueStanding
from league.services import build_full_standings_for_season
from result.models import Result
from season.models import Season
from season.queries import (
    get_open_season,
    get_registered_participants,
    get_running_season,
    get_season_progress,
    get_seasons_progress,
    is_profile_registered,
    register,
)
from season.serializer import (
    SeasonSerializer,
    SeasonWithLeaguesSerializer,
)
from season.services import create_leagues, open_registration, rank_participants
from user.models import PlayerProfile


class SeasonRegistrationView(APIView):
    """
    API view for registering the current user for the open season.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            return HttpResponseNotFound("Player profile not found.")
        open_season = get_open_season()
        if not open_season:
            return Response(
                {"detail": "No season is currently open for registration."},
                status=status.HTTP_409_CONFLICT,
            )
        if not is_profile_registered(player_profile, open_season):
            register(player_profile)
            return Response(
                f"Participant {player_profile.profile_name} has been added to the current season."
            )
        return Response(f"Player {player_profile.profile_name} is already registered")


class CurrentSeasonView(APIView):
    """
    API view for retrieving the current active or upcoming season.
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
            {
                "id": season.id,
                "name": season.name,
                "status": season.status,
                "progress": get_season_progress(season),
            },
            status=status.HTTP_200_OK,
        )


class SeasonViewSet(ModelViewSet):
    """
    API viewset for viewing and managing seasons.
    Includes custom actions for starting seasons, viewing winners, and registration status.
    """
    queryset = Season.objects.all().order_by("-year", "-month")
    serializer_class = SeasonSerializer
    filterset_fields = ["year", "month", "status"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        seasons_list = list(page) if page is not None else list(queryset)
        progress_map = get_seasons_progress(seasons_list)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
            context={"seasons_progress": progress_map, "request": request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

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
            "current_champion",
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
                    "progress": get_season_progress(season),
                },
                "leagues": payloads,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="seasons-with-leagues")
    def seasons_with_leagues(self, request):
        queryset = self.get_queryset().filter(leagues__isnull=False).distinct()
        seasons_list = list(queryset)
        progress_map = get_seasons_progress(seasons_list)
        serializer = SeasonWithLeaguesSerializer(
            queryset,
            many=True,
            context={"seasons_progress": progress_map, "request": request},
        )
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
        """
        season = get_object_or_404(
            Season.objects.only("id", "year", "month", "status"),
            pk=pk,
        )

        if not season.is_completed:
            return Response(
                {
                    "season": {
                        "id": season.id,
                        "name": season.name,
                        "status": season.status,
                    },
                    "winners": [],
                },
                status=status.HTTP_200_OK,
            )

        leagues = League.objects.filter(season_id=season.id).order_by("level", "id")

        standings = (
            LeagueStanding.objects.filter(league__in=leagues)
            .select_related("league", "player_profile", "player_profile__user")
            .order_by("league_id", "-league_points", "-wins", "-second_places", "-third_places", "-tie_break_priority", "id")
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
                            "avatar_shape": getattr(user, "avatar_shape", "squircle")
                            if user
                            else "squircle",
                            "avatar_color": getattr(user, "avatar_color", "")
                            if user
                            else "",
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

    @action(detail=False, methods=["get"], url_path="current-champion")
    def current_champion(self, request):
        """
        GET /seasons/current-champion/

        Returns the level-1 champion for the most recently completed (DONE) season.
        """
        latest_season = (
            Season.objects.filter(status=Season.SeasonStatus.DONE)
            .order_by("-year", "-month", "-id")
            .first()
        )
        if not latest_season:
            return Response(None, status=status.HTTP_200_OK)

        level_1_league = (
            League.objects.filter(season=latest_season, level=1)
            .order_by("id")
            .first()
        )
        if not level_1_league:
            return Response(None, status=status.HTTP_200_OK)

        winner_standing = (
            LeagueStanding.objects.filter(league=level_1_league)
            .select_related("player_profile", "player_profile__user")
            .order_by("-league_points", "-wins", "-second_places", "-third_places", "-tie_break_priority", "id")
            .first()
        )
        if not winner_standing or not winner_standing.player_profile:
            return Response(None, status=status.HTTP_200_OK)

        profile = winner_standing.player_profile
        user = getattr(profile, "user", None)
        username = getattr(user, "username", None) or profile.profile_name

        return Response(
            {
                "username": username,
                "season_id": latest_season.id,
                "season_name": latest_season.name,
                "profile_id": profile.id,
                "profile_name": profile.profile_name,
                "league_points": winner_standing.league_points,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="open-registration")
    def open_registration(self, request, pk=None):
        season = self.get_object()
        if season.status != Season.SeasonStatus.NEXT:
            return Response(
                {"detail": "Only seasons with status NEXT can be opened for registration."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            open_registration(season)
            return Response(
                {"detail": "Season opened for registration successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="start-season")
    def start_season(self, request, pk=None):
        season = self.get_object()
        if season.status != Season.SeasonStatus.OPEN:
            return Response(
                {"detail": "Only OPEN seasons can be started manually."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from season_manager import start_new_season

        try:
            start_new_season(season)
            return Response(
                {"detail": "Season started successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="fill-leagues")
    def fill_leagues(self, request, pk=None):
        """
        POST /seasons/{id}/fill-leagues/

        Distributes the season's currently registered participants into
        leagues, reusing the same ranking/promotion logic applied during the
        automated ``start_new_season`` transition, without closing the
        running season or creating the next one. Existing leagues for the
        season are removed and recreated from the current participants.
        """
        season = self.get_object()
        if season.status != Season.SeasonStatus.OPEN:
            return Response(
                {"detail": "Only OPEN seasons can have their leagues filled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Result.objects.filter(season=season).exists():
            return Response(
                {
                    "detail": "Cannot fill leagues because match results already exist for this season."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        participants = list(get_registered_participants(season))
        if not participants:
            return Response(
                {"detail": "No registered participants found for this season."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                League.objects.filter(season=season).delete()
                ranked = rank_participants(season, participants)
                create_leagues(season, ranked)
            return Response(
                {"detail": "Leagues filled successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
