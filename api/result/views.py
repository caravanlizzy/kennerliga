from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from game.models import SelectedGame, ResultConfig, TieBreaker
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
        # Extract POST data
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])
        dry_run = request.query_params.get("dry_run") == "true" or request.data.get("dry_run") is True

        # Validate input structure
        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response(
                {"detail": "You must submit a selected_game and at least two results."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Load SelectedGame, including its Game, League, and Season
        try:
            selected_game = SelectedGame.objects.select_related('game', 'league__season').get(pk=selected_game_id)
        except SelectedGame.DoesNotExist:
            return Response({"detail": "SelectedGame not found."}, status=status.HTTP_404_NOT_FOUND)

        league = selected_game.league
        season = league.season
        game = selected_game.game

        # Load the ResultConfig to determine scoring and tie-breaker rules
        try:
            result_config = ResultConfig.objects.get(game=game)
        except ResultConfig.DoesNotExist:
            return Response({"detail": "ResultConfig not found for this game."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Validate and enrich each submitted result
        serializers = []
        for entry in data:
            # Inject contextual foreign keys
            entry['selected_game'] = selected_game.id
            entry['league'] = league.id
            entry['season'] = season.id

            serializer = ResultSerializer(data=entry, context={"request": request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(serializer)

        # Get validated data from all serializers
        validated = [s.validated_data for s in serializers]

        # Step 2: Identify top scorers
        scores = [v["points"] for v in validated]
        max_score = max(scores)
        tied = [v for v in validated if v["points"] == max_score]

        # Tie-breaking helper: safely parse tie breaker values
        def parse_tb(val):
            try:
                return float(val.get("tie_breaker_value") or -1)
            except (ValueError, TypeError):
                return -1

        decisive_tb = None  # This will store the TieBreaker that resolves the tie

        if len(tied) > 1:
            # Load configured tie-breakers for this game, ordered by priority
            tie_breakers = TieBreaker.objects.filter(result_config=result_config).order_by("order")

            # Step 3: Try tie-breakers one by one
            for tb in tie_breakers:
                # Parse each tied player's tie_breaker_value
                tb_values = [(r, parse_tb(r)) for r in tied]
                max_tb = max(val for _, val in tb_values)
                tied = [r for r, val in tb_values if val == max_tb]

                if len(tied) == 1:
                    decisive_tb = tb  # Tie resolved by this TieBreaker
                    break

            # Step 4: Still tied after all tie-breakers → return early
            if len(tied) > 1:
                return Response(
                    {
                        "detail": "Still tied after all tie-breakers.",
                        "tied_players": [r["player_profile"].id for r in tied],
                        "unresolved_tie": True
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            # Optional: record which tie-breaker resolved the tie
            for s in serializers:
                if s.validated_data in tied:
                    s._decisive_tie_breaker = decisive_tb  # store for later injection

        # Step 5: Dry-run mode → only preview, don’t save
        if dry_run:
            return Response(
                {
                    "detail": "No tie detected. Would have saved results.",
                    "dry_run": True,
                    "results_preview": [s.data for s in serializers],
                },
                status=status.HTTP_200_OK,
            )

        # Step 6: Save all results transactionally
        with transaction.atomic():
            saved_results = []
            for s in serializers:
                # Inject the tie-breaker that resolved the tie (if any)
                if hasattr(s, "_decisive_tie_breaker"):
                    s.validated_data["decisive_tie_breaker"] = s._decisive_tie_breaker
                saved_results.append(s.save())

        # Step 7: Return the saved results
        return Response(
            ResultSerializer(saved_results, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request):
        season_id = request.query_params.get("season")
        league_id = request.query_params.get("league")
        selected_game_id = request.query_params.get("selected_game")

        if not all([season_id, league_id, selected_game_id]):
            return Response(
                {"detail": "season, league, and selected_game parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = Result.objects.filter(
            season_id=season_id,
            league_id=league_id,
            selected_game_id=selected_game_id,
        )

        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





