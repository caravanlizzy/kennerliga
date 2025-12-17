from collections import defaultdict

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from game.models import SelectedGame, ResultConfig, TieBreaker
from league.models import GameStanding
from league.serializer import GameStandingSerializer
from season.models import Season
from season.serializer import SeasonSerializer
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot
from .models import Result
from .serializers import ResultSerializer

# ViewSet to manage a users result, mainly useful for admins
# The frontend would usually post a set of results => 1 result per player in the league
# which is handled in a separate ViewSet (MathResultViewSet)
class ResultViewSet(ModelViewSet):
    """
    Handles the operations related to the Result model.

    This class is a ViewSet for the Result model and provides
    CRUD operations for handling Result data. It is based on
    Django Rest Framework's ModelViewSet and integrates
    filtering functionality for specified fields.

    Attributes:
        queryset: Defines the default queryset for the ModelViewSet.
        serializer_class: Specifies the serializer to be used for
            serializing and deserializing Result objects.
        filterset_fields: Lists the fields that can be used for
            filtering results during API requests.
    """
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ['selected_game']


class MatchResultViewSet(ViewSet):
    """
    Handles operations for match results, including creation of results and resolving tie-breakers.

    This class provides the functionality to validate, process, and save match results, ensuring that
    all necessary data is supplied and adheres to expected business rules. It handles the detection
    and resolution of ties based on defined tie-breaker rules within a game configuration. The class
    also interacts with multiple related models such as `SelectedGame`, `ResultConfig`, and
    `TieBreaker` to validate and process results. If results meet all constraints, they are saved,
    and necessary snapshots for the game and league standings are rebuilt.

    Attributes:
        permission_classes: Specifies the permission classes required to access this viewset.
    """
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])
        requested_tb_id = (request.data.get("tiebreaker") or {}).get("id")

        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response(
                {"detail": "You must submit a selected_game and at least two results."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- Load SelectedGame + related
        try:
            selected_game = (
                SelectedGame.objects
                .select_related("game", "league__season")
                .get(pk=selected_game_id)
            )
        except SelectedGame.DoesNotExist:
            return Response(
                {"detail": "SelectedGame not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        league = selected_game.league
        season = league.season
        game = selected_game.game

        expected_result_count = league.members.count()
        if len(data) != expected_result_count:
            return Response(
                {"detail": f"Expected {expected_result_count} results, got {len(data)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- Load ResultConfig
        try:
            result_config = ResultConfig.objects.get(game=game)
        except ResultConfig.DoesNotExist:
            return Response(
                {"detail": "ResultConfig not found for this game."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        use_points = result_config.has_points
        base_field = "points" if use_points else "position"

        # ---- Validate rows via serializer
        serializers = []
        seen = set()
        for entry in data:
            # these are implicit in ResultSerializer.create but harmless here
            entry["selected_game"] = selected_game.id
            entry["league"] = league.id
            entry["season"] = season.id

            pid = entry.get("player_profile")
            if pid in seen:
                return Response(
                    {"detail": f"Duplicate player_profile {pid} in payload."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen.add(pid)

            s = ResultSerializer(data=entry, context={"request": request})
            if not s.is_valid():
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(s)

        rows = [s.validated_data for s in serializers]

        # ---- Extra validation for points vs position
        if use_points:
            # serializer.validate ensures "points" is present, but we can check None
            missing_points = [r["player_profile"].id for r in rows if r.get("points") is None]
            if missing_points:
                return Response(
                    {
                        "detail": "This game uses points. Missing 'points' for some players.",
                        "missing_players": missing_points,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            positions = [r.get("position") for r in rows]
            if any(p is None for p in positions):
                return Response(
                    {
                        "detail": "This game does not use points. You must submit 'position' for all players."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # optional strict check: positions are 1..N and unique
            try:
                int_positions = [int(p) for p in positions]
            except (TypeError, ValueError):
                return Response(
                    {"detail": "Positions must be integers."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(set(int_positions)) != expected_result_count or not all(
                1 <= p <= expected_result_count for p in int_positions
            ):
                return Response(
                    {
                        "detail": "Positions must be a unique sequence from 1 to number of players."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ---- Tie-breakers (highest order first)
        tbs = list(TieBreaker.objects.filter(result_config=result_config).order_by("-order"))
        tb_index_by_id = {tb.id: idx for idx, tb in enumerate(tbs)}

        def fnum(x, default=None):
            try:
                return float(x)
            except (TypeError, ValueError):
                return default

        # Build a key for sorting/grouping up to a given TB level (inclusive)
        # level=-1 => only base metric (points or position)
        def key_up_to(row, level: int):
            base_val = fnum(row.get(base_field), 0)

            # For points: higher is better (sort descending)
            # For position: lower is better (sort ascending)
            if use_points:
                key = [-base_val]
            else:
                key = [base_val]

            for i in range(level + 1):
                if i < 0:
                    continue

                tb = tbs[i]
                val = fnum(row.get("tie_breaker_value"))

                # Missing values should keep players grouped as "still tied" until provided
                if val is None:
                    key.append(float("inf"))
                    continue

                # Apply TB direction:
                # - higher_wins=True  => larger value should rank first (sort desc => negative)
                # - higher_wins=False => smaller value should rank first (sort asc => positive)
                key.append(-val if tb.higher_wins else val)

            return tuple(key)

        # Group rows by a given level's key; return groups (list of lists)
        def tie_groups_at_level(level: int):
            groups = defaultdict(list)
            for r in rows:
                groups[key_up_to(r, level)].append(r)
            # Only return groups with ties (size > 1)
            return [g for g in groups.values() if len(g) > 1]

        # Helper for sorting tie groups (for response)
        def group_sort_key(grp):
            base_val = fnum(grp[0].get(base_field), 0)
            return -base_val if use_points else base_val

        # ---- First pass: no specific tie-breaker requested yet
        if requested_tb_id is None:
            # Did we tie on raw base metric anywhere?
            g = tie_groups_at_level(-1)
            if not g:
                # No ties at any position → persist, mark resolved
                with transaction.atomic():
                    saved = []
                    for s in serializers:
                        s.validated_data["tie_breaker_resolved"] = True
                        saved.append(s.save())

                    # you might later want a different win_mode for position-based games
                    rebuild_game_snapshot(selected_game, win_mode="count_top_block")
                    rebuild_league_snapshot(league, win_mode="count_top_block")

                standings = (
                    GameStanding.objects
                    .filter(league=league, selected_game=selected_game.id)
                    .select_related("player_profile")
                    .order_by("rank", "player_profile__profile_name")
                )
                return Response(
                    {
                        "results": ResultSerializer(saved, many=True).data,
                        "game_standings": GameStandingSerializer(standings, many=True).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            if not tbs:
                # Ties exist but no TB configured
                return Response(
                    {
                        "detail": "Tie detected but no tie-breakers configured.",
                        "unresolved_tie": True,
                        "tie_groups": [
                            {
                                "points": grp[0].get("points"),
                                "position": grp[0].get("position"),
                                "players": [r["player_profile"].id for r in grp],
                            }
                            for grp in sorted(g, key=group_sort_key)
                        ],
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            # Ask for the highest-order TB for ALL tie groups
            next_tb = tbs[0]
            return Response(
                {
                    "detail": "Tie detected. Provide values for the required tie-breaker.",
                    "required_tie_breaker": {
                        "id": next_tb.id,
                        "name": next_tb.name,
                        "order": next_tb.order,
                        "higher_wins": next_tb.higher_wins,
                    },
                    "unresolved_tie": True,
                    "tie_groups": [
                        {
                            "points": grp[0].get("points"),
                            "position": grp[0].get("position"),
                            "players": [r["player_profile"].id for r in grp],
                        }
                        for grp in sorted(g, key=group_sort_key)
                    ],
                },
                status=status.HTTP_202_ACCEPTED,
            )

        # ---- We are applying a specific TB level
        if requested_tb_id not in tb_index_by_id:
            return Response(
                {"detail": "Requested tie-breaker is invalid for this game."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        level = tb_index_by_id[requested_tb_id]

        # Ensure ALL players that are currently tied at level-1 supplied a value
        needing_values = tie_groups_at_level(level - 1)
        needing_pids = {r["player_profile"].id for grp in needing_values for r in grp}

        missing = [
            r["player_profile"].id
            for r in rows
            if r["player_profile"].id in needing_pids and fnum(r.get("tie_breaker_value")) is None
        ]
        if missing:
            return Response(
                {
                    "detail": "Provide tie_breaker_value for all players in the listed tie groups.",
                    "required_tie_breaker": {"id": requested_tb_id},
                    "missing_players": missing,
                    "tie_groups": [
                        {
                            "points": grp[0].get("points"),
                            "position": grp[0].get("position"),
                            "players": [r["player_profile"].id for r in grp],
                        }
                        for grp in sorted(needing_values, key=group_sort_key)
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # After values provided, check if any ties remain at this level
        remaining = tie_groups_at_level(level)
        if remaining:
            # Still tied at this TB → ask next, if any
            if level + 1 < len(tbs):
                next_tb = tbs[level + 1]
                return Response(
                    {
                        "detail": "Still tied after this tie-breaker. Provide the next one.",
                        "required_tie_breaker": {
                            "id": next_tb.id,
                            "name": next_tb.name,
                            "order": next_tb.order,
                            "higher_wins": next_tb.higher_wins,
                        },
                        "unresolved_tie": True,
                        "tie_groups": [
                            {
                                "points": grp[0].get("points"),
                                "position": grp[0].get("position"),
                                "players": [r["player_profile"].id for r in grp],
                            }
                            for grp in sorted(remaining, key=group_sort_key)
                        ],
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            # No more TBs to apply; accept unresolved tie
            return Response(
                {
                    "detail": "Still tied after all tie-breakers.",
                    "unresolved_tie": True,
                    "tie_groups": [
                        {
                            "points": grp[0].get("points"),
                            "position": grp[0].get("position"),
                            "players": [r["player_profile"].id for r in grp],
                        }
                        for grp in sorted(remaining, key=group_sort_key)
                    ],
                },
                status=status.HTTP_202_ACCEPTED,
            )

        # ---- No ties remain anywhere → persist
        needing_set = {r["player_profile"].id for grp in needing_values for r in grp}
        decisive_tb = tbs[level]

        with transaction.atomic():
            saved = []

            def full_key(r):
                base_val = fnum(r.get(base_field), 0)
                key = [-base_val] if use_points else [base_val]
                for tb_idx in range(level + 1):
                    tb = tbs[tb_idx]
                    v = fnum(r.get("tie_breaker_value"))
                    if v is None:
                        key.append(float("inf"))
                    else:
                        key.append(-v if tb.higher_wins else v)
                return tuple(key)

            # Mark flags and save
            for s in serializers:
                pid = s.validated_data["player_profile"].id
                if pid in needing_set:
                    s.validated_data["decisive_tie_breaker"] = decisive_tb
                s.validated_data["tie_breaker_resolved"] = True
                saved.append(s.save())

            rebuild_game_snapshot(selected_game, win_mode="count_top_block")
            rebuild_league_snapshot(league, win_mode="count_top_block")

        standings = (
            GameStanding.objects
            .filter(league=league, selected_game=selected_game.id)
            .select_related("player_profile")
            .order_by("rank", "player_profile__profile_name")
        )
        return Response(
            {
                "results": ResultSerializer(saved, many=True).data,
                "game_standings": GameStandingSerializer(standings, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def list(self, request):
        """
        GET /api/result/match-results/?season=<id>&league=<id>&selected_game=<id>
        Returns raw Result rows for that selected_game in that league/season.
        """
        season_id = request.query_params.get("season")
        league = request.query_params.get("league")
        selected_game_id = request.query_params.get("selected_game")

        if not all([season_id, league, selected_game_id]):
            return Response(
                {"detail": "season, league, and selected_game parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Result.objects.filter(
            season_id=season_id,
            league=league,
            selected_game_id=selected_game_id,
        )
        return Response(ResultSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    # Optional: keep a detail endpoint by primary key if you need it
    def retrieve(self, request, pk=None):
        """
        GET /api/result/match-results/{pk}/  -> one Result by its ID
        """
        try:
            obj = Result.objects.get(pk=pk)
        except Result.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResultSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="seasons-with-results")
    def seasons_with_results(self, request):
        """
        GET /api/result/match-results/seasons-with-results/
        Returns all Season records that have at least one Result.
        """
        seasons = Season.objects.filter(results__isnull=False).distinct()
        return Response(SeasonSerializer(seasons, many=True).data, status=status.HTTP_200_OK)



