from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Result
from .serializers import ResultSerializer
from league.models import League
from game.models import ResultConfig, TieBreaker


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Optional filters
        league_id = self.request.query_params.get('league')
        season_id = self.request.query_params.get('season')
        player_id = self.request.query_params.get('player_profile')

        if league_id:
            queryset = queryset.filter(league_id=league_id)
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        if player_id:
            queryset = queryset.filter(player_profile_id=player_id)

        return queryset

    def perform_create(self, serializer):
        result = serializer.save()

        # Optional: trigger tie-breaker assignment logic if league is now full
        self.maybe_assign_decisive_tiebreaker(result.league)

    def maybe_assign_decisive_tiebreaker(self, league: League):
        results = list(Result.objects.filter(league=league))
        expected_players = league.members.count()

        if len(results) < expected_players:
            return  # Not all results in yet

        config = ResultConfig.objects.filter(game=results[0].selected_game.game).first()
        if not config:
            return

        tiebreakers = config.tiebreaker_set.all().order_by('order')

        for tb in tiebreakers:
            values = set(r.tie_breaker_value for r in results if r.tie_breaker_value)
            if len(values) > 1:
                for r in results:
                    r.decisive_tie_breaker = tb
                    r.save(update_fields=['decisive_tie_breaker'])
                break
