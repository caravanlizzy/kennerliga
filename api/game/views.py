from django.db.models.functions import Lower
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption, BanDecision
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer, FactionSerializer, \
    TieBreakerSerializer, ResultConfigSerializer, StartingPointSystemSerializer, PlatformSerializer, \
    SelectedGameSerializer, SelectedOptionSerializer, FullGameSerializer, BanDecisionSerializer

from league.services import advance_turn
from league.models import League
from .queries import get_all_games, get_selected_games_for_league


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all().order_by(Lower('name'))
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = get_all_games()
        league_id = self.request.query_params.get("league")
        manage_only = self.request.query_params.get("manage_only", "false").lower() == "true"
        is_admin = self.request.user and self.request.user.is_staff

        if manage_only and is_admin:
            queryset = Game.objects.all()

        if league_id:
            try:
                league = League.objects.get(id=league_id)
                member_count = league.members.count()

                if not (manage_only and is_admin):
                    queryset = queryset.filter(
                        min_players__lte=member_count,
                        max_players__gte=member_count
                    )

                selected_games = get_selected_games_for_league(league).values_list("game_id", flat=True)
                queryset = queryset.exclude(id__in=selected_games)
            except League.DoesNotExist:
                pass

        return queryset.order_by(Lower('name'))


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
    permission_classes = [IsAuthenticated]

class ResultConfigViewSet(ModelViewSet):
    queryset = ResultConfig.objects.all()
    serializer_class = ResultConfigSerializer
    filterset_fields = ['game']
    permission_classes = [IsAuthenticated]


class StartingPointSystemViewSet(ModelViewSet):
    queryset = StartingPointSystem.objects.all()
    serializer_class = StartingPointSystemSerializer
    permission_classes = [IsAuthenticated]


class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticated]


class SelectedGameViewSet(ModelViewSet):
    queryset = SelectedGame.objects.all()
    serializer_class = SelectedGameSerializer
    filterset_fields = ['league', 'profile']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        selected_game = serializer.save()


class BanDecisionViewSet(ModelViewSet):
    queryset = BanDecision.objects.all()
    serializer_class = BanDecisionSerializer
    filterset_fields = ['league']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ban_decision = serializer.save()


class SelectedOptionViewSet(ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer
    permission_classes = [IsAuthenticated]


class FullGameViewSet(ModelViewSet):
    queryset = Game.objects.all().prefetch_related('options__choices')
    serializer_class = FullGameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        manage_only = self.request.query_params.get("manage_only", "false").lower() == "true"
        is_admin = self.request.user and self.request.user.is_staff

        if not (manage_only and is_admin):
            queryset = queryset.filter(selectable=True)

        return queryset
