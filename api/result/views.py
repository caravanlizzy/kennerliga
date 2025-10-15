from collections import defaultdict

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from game.models import SelectedGame, ResultConfig, TieBreaker
from league.models import GameStanding
from league.serializer import GameStandingSerializer
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot
from .models import Result
from .serializers import ResultSerializer

# ViewSet to manage a users result, mainly useful for admins
# The frontend would usually post a set of results => 1 result per player in the league
# which is handled in a separate ViewSet (MathResultViewSet)
class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ['selected_game']


class MatchResultViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])
        requested_tb_id = (request.data.get("tiebreaker") or {}).get("id")

        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response({"detail": "You must submit a selected_game and at least two results."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_game = (
                SelectedGame.objects
                .select_related('game', 'league__season')
                .get(pk=selected_game_id)
            )
        except SelectedGame.DoesNotExist:
            return Response({"detail": "SelectedGame not found."}, status=status.HTTP_404_NOT_FOUND)

        league = selected_game.league
        season = league.season
        game = selected_game.game

        expected_result_count = league.members.count()
        if len(data) != expected_result_count:
            return Response({"detail": f"Expected {expected_result_count} results, got {len(data)}."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            result_config = ResultConfig.objects.get(game=game)
        except ResultConfig.DoesNotExist:
            return Response({"detail": "ResultConfig not found for this game."}, status=status.HTTP_400_BAD_REQUEST)

        # ---- Validate rows via serializer
        serializers = []
        seen = set()
        for entry in data:
            entry['selected_game'] = selected_game.id
            entry['league'] = league.id
            entry['season'] = season.id

            pid = entry.get("player_profile")
            if pid in seen:
                return Response({"detail": f"Duplicate player_profile {pid} in payload."},
                                status=status.HTTP_400_BAD_REQUEST)
            seen.add(pid)

            s = ResultSerializer(data=entry, context={"request": request})
            if not s.is_valid():
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(s)

        rows = [s.validated_data for s in serializers]

        # ---- Tie-breakers (highest order first)
        tbs = list(TieBreaker.objects.filter(result_config=result_config).order_by('-order'))
        tb_index_by_id = {tb.id: idx for idx, tb in enumerate(tbs)}

        def fnum(x, default=None):
            try:
                return float(x)
            except (TypeError, ValueError):
                return default

        # Build a key for sorting/grouping up to a given TB level (inclusive)
        # level=-1 => only points
        def key_up_to(row, level):
            key = [-fnum(row["points"], 0)]  # descending points
            for i in range(level + 1):
                if i < 0:  # no TBs yet
                    continue
                val = fnum(row.get("tie_breaker_value"))
                # Missing values sort as smallest so they group as ties until provided
                key.append(-val if val is not None else float('inf'))
            return tuple(key)

        # Group rows by a given level's key; return groups (list of lists)
        def tie_groups_at_level(level):
            groups = defaultdict(list)
            for r in rows:
                groups[key_up_to(r, level)].append(r)
            # Only return groups with ties (size > 1)
            return [g for g in groups.values() if len(g) > 1]

        # Determine which TB level we are processing now
        if requested_tb_id is None:
            # First pass: did we tie on raw points anywhere?
            g = tie_groups_at_level(-1)
            if not g:
                # No ties at any position → persist, mark resolved
                with transaction.atomic():
                    saved = []
                    for s in serializers:
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
                    status=status.HTTP_201_CREATED
                )

            if not tbs:
                # Ties exist but no TB configured
                return Response(
                    {
                        "detail": "Tie detected but no tie-breakers configured.",
                        "unresolved_tie": True,
                        "tie_groups": [
                            {"points": grp[0]["points"], "players": [r["player_profile"].id for r in grp]}
                            for grp in sorted(g, key=lambda gg: -gg[0]["points"])
                        ],
                    },
                    status=status.HTTP_202_ACCEPTED
                )

            # Ask for the highest-order TB for ALL tie groups
            next_tb = tbs[0]
            return Response(
                {
                    "detail": "Tie detected. Provide values for the required tie-breaker.",
                    "required_tie_breaker": {"id": next_tb.id, "name": next_tb.name, "order": next_tb.order},
                    "unresolved_tie": True,
                    "tie_groups": [
                        {"points": grp[0]["points"], "players": [r["player_profile"].id for r in grp]}
                        for grp in sorted(g, key=lambda gg: -gg[0]["points"])
                    ],
                },
                status=status.HTTP_202_ACCEPTED
            )

        # We are applying a specific TB level
        if requested_tb_id not in tb_index_by_id:
            return Response({"detail": "Requested tie-breaker is invalid for this game."},
                            status=status.HTTP_400_BAD_REQUEST)

        level = tb_index_by_id[requested_tb_id]

        # Ensure ALL players that are currently tied at this level-1 supplied a value
        # 1) find the groups that need this level
        needing_values = tie_groups_at_level(level - 1)
        needing_pids = {r["player_profile"].id for grp in needing_values for r in grp}

        # 2) check values exist for those pids
        missing = [r["player_profile"].id for r in rows
                   if r["player_profile"].id in needing_pids and fnum(r.get("tie_breaker_value")) is None]
        if missing:
            return Response(
                {
                    "detail": "Provide tie_breaker_value for all players in the listed tie groups.",
                    "required_tie_breaker": {"id": requested_tb_id},
                    "missing_players": missing,
                    "tie_groups": [
                        {"points": grp[0]["points"], "players": [r["player_profile"].id for r in grp]}
                        for grp in sorted(needing_values, key=lambda gg: -gg[0]["points"])
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST
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
                        "required_tie_breaker": {"id": next_tb.id, "name": next_tb.name, "order": next_tb.order},
                        "unresolved_tie": True,
                        "tie_groups": [
                            {"points": grp[0]["points"], "players": [r["player_profile"].id for r in grp]}
                            for grp in sorted(remaining, key=lambda gg: -gg[0]["points"])
                        ],
                    },
                    status=status.HTTP_202_ACCEPTED
                )
            # No more TBs to apply; accept unresolved tie
            return Response(
                {
                    "detail": "Still tied after all tie-breakers.",
                    "unresolved_tie": True,
                    "tie_groups": [
                        {"points": grp[0]["points"], "players": [r["player_profile"].id for r in grp]}
                        for grp in sorted(remaining, key=lambda gg: -gg[0]["points"])
                    ],
                },
                status=status.HTTP_202_ACCEPTED
            )

        # No ties remain anywhere → persist. Mark decisive_tie_breaker for any row
        # that *first* broke its prior tie (optional: here we mark the TB used on this step
        # for all players that were part of any group needing_values and are now separated).
        needing_set = {r["player_profile"].id for grp in needing_values for r in grp}
        decisive_tb = tbs[level]

        with transaction.atomic():
            saved = []
            # Sort rows for storage consistency (optional)
            # full key includes all TB levels present
            def full_key(r):
                k = [-fnum(r["points"], 0)]
                for tb_idx in range(level + 1):
                    v = fnum(r.get("tie_breaker_value"), -1.0)
                    k.append(-v)
                return tuple(k)

            # Mark flags
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
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        """
        GET /api/result/match-results/?season=<id>&league=<id>&selected_game=<id>
        Returns raw Result rows for that selected_game in that league/season.
        """
        season_id = request.query_params.get("season")
        league_id = request.query_params.get("league")
        selected_game_id = request.query_params.get("selected_game")

        if not all([season_id, league_id, selected_game_id]):
            return Response(
                {"detail": "season, league, and selected_game parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Result.objects.filter(
            season_id=season_id,
            league_id=league_id,
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



