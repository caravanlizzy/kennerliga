import re
from django.db.models import Count
from django.db.models.functions import Lower
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAdminOrReadOnly
from configuration.services import get_max_same_game_per_year
from game.models import SelectedGame
from league.models import League, LeagueStanding
from league.serializer import LeagueSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season
from season.serializer import SeasonSerializer
from user.models import (
    AVATAR_SHAPE_CHOICES,
    PlayerProfile,
    User,
)
from user.serializers import (
    PlayerProfileSerializer,
    UserSerializer,
)


class UserViewSet(ModelViewSet):
    """
    API viewset for viewing and managing users.
    Includes custom actions for retrieving user-specific leagues, seasons, results, and statistics.
    """
    queryset = User.objects.all().select_related("profile").order_by(Lower("username"))
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Determines the permissions for the current action.
        """
        if self.action in [
            "list",
            "retrieve",
            "user_leagues",
            "user_seasons",
            "user_results",
            "user_statistics",
            "available_years",
            "update_avatar_shape",
            "update_avatar_color",
            "elo",
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(username__iexact=username)
        return qs

    def get_object(self):
        """
        Retrieves a user object by ID or username.
        """
        lookup = self.kwargs["pk"]  # Django REST by default uses pk
        qs = User.objects.all()
        # Try ID first, then username
        user = None
        if lookup.isdigit():
            user = qs.filter(id=lookup).first()
        if user is None:
            user = qs.filter(username__iexact=lookup).first() or qs.filter(username=lookup).first()
        if not user:
            raise NotFound("User not found.")
        return user

    @action(detail=True, methods=["get"], url_path="leagues")
    def user_leagues(self, request, pk=None):
        """
        Custom action to return the leagues for a specific user.
        """
        user = self.get_object()
        leagues = League.objects.filter(members__profile=user.profile)
        serializer = LeagueSerializer(leagues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="seasons")
    def user_seasons(self, request, pk=None):
        """
        Custom action to return the seasons for a specific user.
        """
        user = self.get_object()
        seasons = Season.objects.filter(participants__profile=user.profile)
        serializer = SeasonSerializer(seasons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="results")
    def user_results(self, request, pk=None):
        """
        Custom action to return the results for a specific user.
        """
        user = self.get_object()
        results = Result.objects.filter(player_profile=user.profile)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="avatar-shape")
    def update_avatar_shape(self, request):
        shape = request.data.get("avatar_shape")
        if shape is None and "shape" in request.data:
            shape = request.data.get("shape")
        shape = str(shape).strip() if shape is not None else ""

        valid_shapes = [choice[0] for choice in AVATAR_SHAPE_CHOICES]
        if shape not in valid_shapes:
            return Response(
                {"detail": f"Invalid avatar shape '{shape}'. Choose from: {', '.join(valid_shapes)}."},
                status=400,
            )

        user = request.user
        user.avatar_shape = shape
        user.save(update_fields=["avatar_shape"])
        return Response(UserSerializer(user, context={"request": request}).data)

    @action(detail=False, methods=["patch"], url_path="avatar-color")
    def update_avatar_color(self, request):
        color = request.data.get("avatar_color")
        if color is None and "color" in request.data:
            color = request.data.get("color")
        color = str(color).strip() if color is not None else ""

        if color and color != "auto":
            if not re.match(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", color):
                return Response(
                    {"detail": "Invalid color format. Please provide a valid hex color (e.g. #2563eb) or empty string for auto."},
                    status=400,
                )
        if color == "auto":
            color = ""

        user = request.user
        user.avatar_color = color
        user.save(update_fields=["avatar_color"])
        return Response(UserSerializer(user, context={"request": request}).data)

    @action(detail=True, methods=["post", "patch"], url_path="toggle-admin")
    def toggle_admin(self, request, pk=None):
        """
        POST/PATCH /user/users/{id|username}/toggle-admin/
        Toggles or sets the user's admin status. Admin only.
        Optional payload: {"admin": true/false}
        """
        user = self.get_object()
        if "admin" in request.data:
            make_admin = bool(request.data.get("admin"))
        elif "is_admin" in request.data:
            make_admin = bool(request.data.get("is_admin"))
        elif "is_staff" in request.data:
            make_admin = bool(request.data.get("is_staff"))
        else:
            make_admin = not (user.is_staff or user.is_superuser)

        user.is_staff = make_admin
        user.is_superuser = make_admin
        user.save(update_fields=["is_staff", "is_superuser"])
        return Response(UserSerializer(user, context={"request": request}).data)

    def perform_update(self, serializer):
        if "admin" in self.request.data:
            make_admin = bool(self.request.data.get("admin"))
            serializer.instance.is_staff = make_admin
            serializer.instance.is_superuser = make_admin
        elif "is_admin" in self.request.data:
            make_admin = bool(self.request.data.get("is_admin"))
            serializer.instance.is_staff = make_admin
            serializer.instance.is_superuser = make_admin
        elif "is_staff" in self.request.data:
            make_admin = bool(self.request.data.get("is_staff"))
            serializer.instance.is_staff = make_admin
            serializer.instance.is_superuser = make_admin
        serializer.save()

    @action(detail=False, methods=["get"], url_path="available-years")
    def available_years(self, request):
        """
        GET /api/user/users/available-years/
        Returns list of years that have data (seasons with match results).
        """
        years = list(
            Season.objects.filter(results__isnull=False)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        if not years:
            years = list(
                Season.objects.values_list("year", flat=True)
                .distinct()
                .order_by("-year")
            )
        if not years:
            years = [timezone.now().year]
        return Response(years)

    @action(detail=True, methods=["get"], url_path="statistics")
    def user_statistics(self, request, pk=None):
        """
        GET /user/users/{id|username}/statistics/?year=2026
        Returns aggregated league and game statistics for the user.
        """
        user = self.get_object()
        profile = user.profile

        # 0. Get year from query params
        year_param = request.query_params.get("year")
        if year_param and str(year_param).lower() in ["all", "none", ""]:
            selected_year = None
        else:
            try:
                selected_year = int(year_param) if year_param else timezone.now().year
            except ValueError:
                selected_year = timezone.now().year

        player_count = request.query_params.get("player_count")
        if player_count and player_count.lower() == "all":
            player_count = None

        raw_years = request.query_params.getlist("years") + request.query_params.getlist("years[]")
        if not raw_years and "years" in request.query_params:
            raw_years = [request.query_params.get("years")]
        if not raw_years and "years[]" in request.query_params:
            raw_years = [request.query_params.get("years[]")]

        parsed_years = []
        for item in raw_years:
            if isinstance(item, str) and "," in item:
                for part in item.split(","):
                    if part.strip().isdigit():
                        parsed_years.append(int(part.strip()))
            elif str(item).isdigit():
                parsed_years.append(int(item))

        exclude_2p_only = (
            request.query_params.get("exclude_2p_only", "").lower() in ["true", "1"]
        )
        exclude_3p_only = (
            request.query_params.get("exclude_3p_only", "").lower() in ["true", "1"]
        )

        # 1. Game Statistics (Aggregated)
        results = Result.objects.filter(player_profile=profile).select_related(
            "selected_game__game"
        )
        if parsed_years:
            results = results.filter(season__year__in=parsed_years)

        parsed_pcs = []
        if player_count:
            if isinstance(player_count, str):
                tokens = player_count.split(",")
            elif isinstance(player_count, (list, tuple, set)):
                tokens = list(player_count)
            else:
                tokens = [player_count]
            for token in tokens:
                t = str(token).lower().replace("p", "").strip()
                if t.isdigit():
                    parsed_pcs.append(int(t))

        if parsed_pcs or exclude_2p_only or exclude_3p_only:
            sg_counts = Result.objects.values("selected_game_id").annotate(cnt=Count("id"))
            if parsed_pcs:
                sg_counts = sg_counts.filter(cnt__in=parsed_pcs)
            if exclude_2p_only:
                sg_counts = sg_counts.filter(cnt__gt=2)
            if exclude_3p_only:
                sg_counts = sg_counts.exclude(cnt=3)
            results = results.filter(selected_game_id__in=sg_counts.values("selected_game_id"))

        # Aggregated game metrics (overall)
        overall_stats = {
            "total_games": results.count(),
            "wins": 0,
            "podiums": 0,  # 1, 2, 3
            "avg_pos": 0,
            "positions": {},  # Distribution of positions across all games
        }

        pos_sum = 0
        positioned_games = 0
        for r in results:
            if r.position is not None:
                positioned_games += 1
                pos_sum += r.position
                overall_stats["positions"][r.position] = (
                    overall_stats["positions"].get(r.position, 0) + 1
                )
                if r.position == 1:
                    overall_stats["wins"] += 1
                if r.position <= 3:
                    overall_stats["podiums"] += 1

        if positioned_games > 0:
            overall_stats["avg_pos"] = pos_sum / positioned_games

        # Per-game statistics
        stats_map = {}
        for r in results:
            game_name = (
                r.selected_game.game.name
                if r.selected_game and r.selected_game.game
                else f"Game {r.selected_game_id}"
            )
            if game_name not in stats_map:
                stats_map[game_name] = {"name": game_name, "positions": [], "wins": 0}

            if r.position is not None:
                stats_map[game_name]["positions"].append(r.position)
                if r.position == 1:
                    stats_map[game_name]["wins"] += 1

        game_stats = []
        for g in stats_map.values():
            count = len(g["positions"])
            game_stats.append(
                {
                    "name": g["name"],
                    "winRate": (g["wins"] / count * 100) if count > 0 else 0,
                    "avgPos": (sum(g["positions"]) / count) if count > 0 else 0,
                    "count": count,
                    "positions": g["positions"],
                }
            )

        # Sort by count descending for the default list
        game_stats.sort(key=lambda x: x["count"], reverse=True)

        # 1b. Picked Games for the selected year (or all time)
        # We only count games that were NOT banned.
        from game.queries import get_successfully_banned_game_ids

        banned_game_ids = get_successfully_banned_game_ids(year=selected_year)

        max_game_limit = get_max_same_game_per_year()

        picked_games_base = SelectedGame.objects.filter(profile=profile)
        if selected_year is not None:
            picked_games_base = picked_games_base.filter(
                league__season__year=selected_year
            )

        picked_games_qs = (
            picked_games_base.exclude(id__in=banned_game_ids)
            .values("game_id", "game__name", "game__platform__name")
            .annotate(count=Count("id"))
            .order_by("-count" if selected_year is None else "game__name", "game__name")
        )

        picked_games = [
            {
                "game_id": item["game_id"],
                "name": item["game__name"],
                "platform": item["game__platform__name"],
                "count": item["count"],
                "limit_exceeded": (
                    item["count"] >= max_game_limit if selected_year is not None else False
                ),
            }
            for item in picked_games_qs
        ]

        # 2. League Statistics (Minimal, as requested to be less prominent)
        standings = LeagueStanding.objects.filter(
            player_profile=profile
        ).select_related("league")
        total_leagues = standings.count()

        # Derive Top 3 games by highest win rate (then by more plays, then by better avg position)
        top_games = sorted(
            game_stats,
            key=lambda x: (
                -(x["winRate"] or 0),  # highest win rate first
                -(x["count"] or 0),  # then more games played
                (x["avgPos"] or 0),  # then lower average position (better)
                x["name"],  # stable final tie-breaker
            ),
        )[:3]

        # Get available years
        available_years = list(Season.objects.values_list('year', flat=True).distinct().order_by('-year'))
        if not available_years:
            available_years = [timezone.now().year]

        from services.elo import get_elo_rank
        from result.models import EloChange
        from result.serializers import EloChangeSerializer

        elo_changes_qs = EloChange.objects.filter(player_profile=profile).select_related(
            "selected_game__game", "season", "league"
        ).order_by("-created_at", "-id")
        recent_changes = list(elo_changes_qs[:20])
        recent_deltas = [c.delta for c in recent_changes[:5]]

        elo_data = {
            "rating": profile.elo_rating if profile else 1500.0,
            "rank": get_elo_rank(profile),
            "history": EloChangeSerializer(recent_changes, many=True).data,
            "recent_deltas": recent_deltas,
        }

        from result.queries import get_game_records_map

        game_records = get_game_records_map()

        player_record_results = (
            Result.objects.filter(player_profile=profile, points__gte=2)
            .select_related("selected_game__game__platform")
            .order_by("selected_game__game__name")
        )
        held_records_map = {}
        for r in player_record_results:
            if not r.selected_game or not r.selected_game.game:
                continue
            g = r.selected_game.game
            if g.id in game_records and r.points == game_records[g.id]:
                if g.id not in held_records_map:
                    held_records_map[g.id] = {
                        "game_id": g.id,
                        "game_name": g.name,
                        "record_score": r.points,
                        "platform": g.platform.name if g.platform else None,
                    }
        records = sorted(held_records_map.values(), key=lambda x: x["game_name"])

        return Response(
            {
                "overall_stats": overall_stats,
                "league_stats": {
                    "totalLeagues": total_leagues,
                },
                "game_stats": game_stats,
                "top_games": top_games,
                "picked_games": picked_games,
                "records": records,
                "max_game_limit": max_game_limit,
                "available_years": available_years,
                "elo": elo_data,
            }
        )

    @action(detail=True, methods=["get"], url_path="elo")
    def elo(self, request, pk=None):
        user = self.get_object()
        profile = getattr(user, "profile", None)
        if not profile:
            return Response(
                {"detail": "No profile found for this user."}, status=404
            )

        from services.elo import get_elo_rank
        from result.models import EloChange
        from result.serializers import EloChangeSerializer

        elo_changes = EloChange.objects.filter(
            player_profile=profile
        ).select_related("selected_game__game", "season", "league").order_by("-created_at", "-id")

        return Response(
            {
                "rating": profile.elo_rating,
                "rank": get_elo_rank(profile),
                "history": EloChangeSerializer(elo_changes, many=True).data,
                "recent_deltas": list(elo_changes.values_list("delta", flat=True)[:5]),
            }
        )


class PlayerProfileViewSet(ModelViewSet):
    """
    API viewset for viewing and managing player profiles.
    """
    queryset = PlayerProfile.objects.select_related("user").all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Filters player profiles, optionally by whether they have an associated user.
        """
        queryset = PlayerProfile.objects.select_related("user").all()

        # Check for user__isnull query parameter
        user_isnull = self.request.query_params.get("user__isnull", None)

        if user_isnull is not None:
            # Strip whitespace and slashes, then convert to lowercase
            user_isnull = user_isnull.strip().strip("/").lower()

            if user_isnull in ["true", "1", "yes"]:
                queryset = queryset.filter(user__isnull=True)
            elif user_isnull in ["false", "0", "no"]:
                queryset = queryset.filter(user__isnull=False)

        return queryset.order_by(Lower("profile_name"))
