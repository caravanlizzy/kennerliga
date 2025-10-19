from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from datetime import datetime

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption, BanDecision
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer, FactionSerializer, \
    TieBreakerSerializer, ResultConfigSerializer, StartingPointSystemSerializer, PlatformSerializer, \
    SelectedGameSerializer, SelectedOptionSerializer, FullGameSerializer, BanDecisionSerializer

from league.services import LeagueService


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Game.objects.all()
        league_id = self.request.query_params.get("league")  # Query param to specify the league

        # Ensure league_id is provided to apply filtering
        if league_id:
            # Exclude games selected by any player in the league
            selected_games = SelectedGame.objects.filter(
                league_id=league_id
            ).values_list("game_id", flat=True)
            queryset = queryset.exclude(id__in=selected_games)

        return queryset


class GameOptionViewSet(ModelViewSet):
    queryset = GameOption.objects.all()
    serializer_class = GameOptionSerializer
    filterset_fields = ['game']
    permission_classes = [IsAuthenticated]


class GameOptionChoiceViewSet(ModelViewSet):
    queryset = GameOptionChoice.objects.all()
    serializer_class = GameOptionChoiceSerializer
    filterset_fields = ['option']
    permission_classes = [IsAuthenticated]


class FactionViewSet(ModelViewSet):
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer
    filterset_fields = ['game']


class TieBreakerViewSet(ModelViewSet):
    queryset = TieBreaker.objects.all()
    serializer_class = TieBreakerSerializer
    filterset_fields = ['result_config']


class ResultConfigViewSet(ModelViewSet):
    queryset = ResultConfig.objects.all()
    serializer_class = ResultConfigSerializer
    filterset_fields = ['game']


class StartingPointSystemViewSet(ModelViewSet):
    queryset = StartingPointSystem.objects.all()
    serializer_class = StartingPointSystemSerializer


class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class SelectedGameViewSet(ModelViewSet):
    queryset = SelectedGame.objects.all()
    serializer_class = SelectedGameSerializer
    filterset_fields = ['league', '']

    def perform_create(self, serializer):
        selected_game = serializer.save()
        league = selected_game.league
        LeagueService(league).advance_turn()


class BanDecisionViewSet(ModelViewSet):
    queryset = BanDecision.objects.all()
    serializer_class = BanDecisionSerializer
    filterset_fields = ['league']

    def perform_create(self, serializer):
        ban_decision = serializer.save()
        league = ban_decision.league

        LeagueService(league).advance_turn()


class SelectedOptionViewSet(ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer


class FullGameViewSet(ModelViewSet):
    queryset = Game.objects.all().prefetch_related('options__choices')
    serializer_class = FullGameSerializer
    permission_classes = [IsAuthenticated]
