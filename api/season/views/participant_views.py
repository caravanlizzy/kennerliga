from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from result.models import Result
from season.models import Season, SeasonParticipant
from season.queries import get_open_season, get_running_season
from season.serializer import (
    SeasonParticipantSerializer,
    SeasonSerializer,
)
from season.services import build_league_projection
from user.models import PlayerProfile


class SeasonParticipantViewSet(ModelViewSet):
    """
    API viewset for managing participants in a season.
    Supports listing participants, projecting league distributions, and retrieving current participants.
    """
    queryset = (
        SeasonParticipant.objects.select_related("season", "profile")
        .prefetch_related("leagues_member")
        .order_by("-season__year", "-season__month", "-season_id")
    )
    serializer_class = SeasonParticipantSerializer
    filterset_fields = ["season", "profile", "profile__profile_name"]

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "projected_leagues",
            "preview_leagues",
            "current",
        ]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a season participant only if no match results exist for them in this season.
        """
        instance = self.get_object()

        if Result.objects.filter(
            season_id=instance.season_id, player_profile_id=instance.profile_id
        ).exists():
            return Response(
                {
                    "detail": "Cannot remove participant because match results already exist for this player in this season."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

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
        """
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
                {
                    "season": None,
                    "leagues": [],
                    "newcomers": [],
                    "active_participants": [],
                    "missing_participants": [],
                    "unprojected_participants": [],
                },
                status=200,
            )

        participants = list(
            SeasonParticipant.objects.filter(season=season).select_related(
                "profile", "profile__user"
            )
        )
        profiles = [sp.profile for sp in participants]
        projection = build_league_projection(profiles)

        active_participants = [
            {
                "id": sp.id,
                "profile": sp.profile_id,
                "profile_name": sp.profile.profile_name,
                "username": getattr(
                    getattr(sp.profile, "user", None), "username", None
                ),
            }
            for sp in participants
        ]

        prev = self._previous_season_for(season)
        missing_participants = []
        if prev:
            current_profile_ids = set(sp.profile_id for sp in participants)
            prev_profile_ids = list(
                SeasonParticipant.objects.filter(season=prev).values_list(
                    "profile_id", flat=True
                )
            )
            missing_ids = [
                pid for pid in prev_profile_ids if pid not in current_profile_ids
            ]
            if missing_ids:
                missing_profiles = PlayerProfile.objects.select_related(
                    "user"
                ).filter(id__in=missing_ids)
                missing_participants = [
                    {
                        "profile": p.id,
                        "profile_name": p.profile_name,
                        "username": getattr(
                            getattr(p, "user", None), "username", None
                        ),
                    }
                    for p in missing_profiles
                ]

        projected_profile_ids = set()
        for lg in projection["leagues"]:
            for m in lg.get("members", []):
                projected_profile_ids.add(m["profile"])
        for m in projection["newcomers"]:
            projected_profile_ids.add(m["profile"])

        unprojected_participants = [
            p
            for p in active_participants
            if p["profile"] not in projected_profile_ids
        ]

        return Response(
            {
                "season": {
                    "id": season.id,
                    "name": season.name,
                    "status": season.status,
                },
                "leagues": projection["leagues"],
                "newcomers": projection["newcomers"],
                "active_participants": active_participants,
                "missing_participants": missing_participants,
                "unprojected_participants": unprojected_participants,
            },
            status=200,
        )

    @action(detail=False, methods=["post"], url_path="preview-leagues")
    def preview_leagues(self, request):
        """
        POST /season-participants/preview-leagues/
        Body: {"profile_ids": [1, 2, 3, ...]}
        """
        profile_ids = request.data.get("profile_ids") or []
        try:
            profile_ids = [int(pid) for pid in profile_ids]
        except (TypeError, ValueError):
            return Response(
                {"detail": "profile_ids must be a list of integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profiles_by_id = PlayerProfile.objects.select_related("user").in_bulk(
            profile_ids
        )
        # Preserve the order the ids were given in, ignore unknown ids.
        profiles = [
            profiles_by_id[pid] for pid in profile_ids if pid in profiles_by_id
        ]

        projection = build_league_projection(profiles)

        return Response(
            {
                "leagues": projection["leagues"],
                "newcomers": projection["newcomers"],
            },
            status=200,
        )

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """
        GET /season-participants/current/
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
