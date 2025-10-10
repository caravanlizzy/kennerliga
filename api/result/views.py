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
        # ---- Extract POST data
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])

        # ---- Validate input structure
        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response(
                {"detail": "You must submit a selected_game and at least two results."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- Load SelectedGame (with game + league + season context)
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

        # ---- Load ResultConfig (scoring / tie-breaker rules selection)
        try:
            result_config = ResultConfig.objects.get(game=game)
        except ResultConfig.DoesNotExist:
            return Response({"detail": "ResultConfig not found for this game."}, status=status.HTTP_400_BAD_REQUEST)

        # ---- Validate & enrich each submitted result
        serializers = []
        seen_players = set()
        for entry in data:
            # inject FKs
            entry['selected_game'] = selected_game.id
            entry['league'] = league.id
            entry['season'] = season.id

            # (optional) ensure each player only appears once for this game payload
            pid = entry.get("player_profile")
            if pid in seen_players:
                return Response({"detail": f"Duplicate player_profile {pid} in payload."},
                                status=status.HTTP_400_BAD_REQUEST)
            seen_players.add(pid)

            s = ResultSerializer(data=entry, context={"request": request})
            if not s.is_valid():
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(s)

        # ---- Get validated rows
        validated = [s.validated_data for s in serializers]

        # ---- Determine top scorers (by raw 'points')
        scores = [v["points"] for v in validated]
        max_score = max(scores)
        tied = [v for v in validated if v["points"] == max_score]

        # helper to parse tie breaker value from a validated row
        def parse_tb(valdict):
            try:
                return float(valdict.get("tie_breaker_value") or -1)
            except (ValueError, TypeError):
                return -1

        decisive_tb = None  # which TieBreaker (if any) resolved the tie

        if len(tied) > 1:
            # apply configured tie-breakers sequentially
            tie_breakers = TieBreaker.objects.filter(result_config=result_config).order_by("order")
            for tb in tie_breakers:
                tb_values = [(row, parse_tb(row)) for row in tied]
                max_tb = max(val for _, val in tb_values)
                tied = [row for row, val in tb_values if val == max_tb]
                if len(tied) == 1:
                    decisive_tb = tb
                    break

            # still tied after all configured TBs → early 202 w/ info
            if len(tied) > 1:
                return Response(
                    {
                        "detail": "Still tied after all tie-breakers.",
                        "tied_players": [r["player_profile"].id for r in tied],
                        "unresolved_tie": True
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            # remember which tie-breaker resolved the tie for the winner row
            for s in serializers:
                if s.validated_data in tied:
                    s._decisive_tie_breaker = decisive_tb  # noqa: SLF001

        # ---- Persist Results + refresh snapshots
        with transaction.atomic():
            saved_results = []
            for s in serializers:
                if hasattr(s, "_decisive_tie_breaker"):
                    s.validated_data["decisive_tie_breaker"] = s._decisive_tie_breaker
                saved_results.append(s.save())

            # Rebuild snapshots (per-game + league)
            rebuild_game_snapshot(selected_game, win_mode="count_top_block")
            rebuild_league_snapshot(league, win_mode="count_top_block")

        # ---- Optionally include the fresh per-game standings in the response
        game_standings_qs = (
            GameStanding.objects
            .filter(league=league, selected_game=selected_game.id)
            .select_related("player_profile")
            .order_by("rank", "player_profile__profile_name")
        )
        payload = {
            "results": ResultSerializer(saved_results, many=True).data,
            "game_standings": GameStandingSerializer(game_standings_qs, many=True).data,
        }
        return Response(payload, status=status.HTTP_201_CREATED)

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



