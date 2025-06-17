from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from game.models import SelectedGame
from .models import Result
from .serializers import ResultSerializer

# ViewSet to manage a users result, mainly useful for admins
# The frontend would usually post a set of results => 1 result per player in the league
# which is handled in a separate ViewSet (MathResultViewSet)
class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


from rest_framework.decorators import action

class MatchResultViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])
        dry_run = request.query_params.get("dry_run") == "true" or request.data.get("dry_run") is True

        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response(
                {"detail": "You must submit a selected_game and at least two results."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            selected_game = SelectedGame.objects.select_related('league__season').get(pk=selected_game_id)
        except SelectedGame.DoesNotExist:
            return Response({"detail": "SelectedGame not found."}, status=status.HTTP_404_NOT_FOUND)

        # Preload related objects
        league = selected_game.league
        season = league.season

        # Validate and enrich each entry
        serializers = []
        for entry in data:
            entry['selected_game'] = selected_game.id
            entry['league'] = league.id
            entry['season'] = season.id

            serializer = ResultSerializer(data=entry, context={"request": request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(serializer)

        validated = [s.validated_data for s in serializers]
        scores = [v["points"] for v in validated]
        max_score = max(scores)
        tied = [v for v in validated if v["points"] == max_score]

        if len(tied) > 1:
            return Response(
                {
                    "detail": "Tie detected. Tie-breaker required.",
                    "dry_run": dry_run,
                    "tied_players": [r["player_profile"].id for r in tied],
                },
                status=status.HTTP_202_ACCEPTED,
            )

        if dry_run:
            return Response(
                {
                    "detail": "No tie detected. Would have saved results.",
                    "dry_run": True,
                    "results_preview": [s.data for s in serializers],
                },
                status=status.HTTP_200_OK,
            )

        with transaction.atomic():
            saved_results = [s.save() for s in serializers]

        return Response(
            ResultSerializer(saved_results, many=True).data,
            status=status.HTTP_201_CREATED,
        )



