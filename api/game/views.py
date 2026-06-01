from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce, Lower
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from game.models import (
    Game,
    GameOption,
    GameOptionChoice,
    Faction,
    TieBreaker,
    ResultConfig,
    StartingPointSystem,
    Platform,
    SelectedGame,
    SelectedOption,
    BanDecision,
)
from game.serializers import (
    GameSerializer,
    GameOptionSerializer,
    GameOptionChoiceSerializer,
    FactionSerializer,
    TieBreakerSerializer,
    ResultConfigSerializer,
    StartingPointSystemSerializer,
    PlatformSerializer,
    SelectedGameSerializer,
    SelectedOptionSerializer,
    FullGameSerializer,
    BanDecisionSerializer,
)

from league.models import League
from result.models import Result
from .queries import (
    get_all_games,
    get_selected_game_ids_for_league_including_related,
    get_max_selected_game_ids_for_profile_in_year_including_related,
)


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all().order_by(Lower("name"))
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = get_all_games()
        league_id = self.request.query_params.get("league")
        manage_only = (
                self.request.query_params.get("manage_only", "false").lower() == "true"
        )
        is_admin = self.request.user and self.request.user.is_staff

        if manage_only and is_admin:
            queryset = Game.objects.all()

        if league_id:
            try:
                league = League.objects.get(id=league_id)
                member_count = league.members.count()

                if not (manage_only and is_admin):
                    queryset = queryset.filter(
                        min_players__lte=member_count, max_players__gte=member_count
                    )

                    selected_games = get_selected_game_ids_for_league_including_related(
                        league
                    )
                    max_selected = (
                        get_max_selected_game_ids_for_profile_in_year_including_related(
                            self.request.user.profile,
                            league.season,
                        )
                    )

                    queryset = queryset.exclude(id__in=selected_games).exclude(
                        id__in=max_selected
                    )
            except League.DoesNotExist:
                pass

        return queryset.order_by(Lower("name"))


class GameOptionViewSet(ModelViewSet):
    queryset = GameOption.objects.all()
    serializer_class = GameOptionSerializer
    filterset_fields = ["game"]
    permission_classes = [IsAuthenticated]


class GameOptionChoiceViewSet(ModelViewSet):
    queryset = GameOptionChoice.objects.all()
    serializer_class = GameOptionChoiceSerializer
    filterset_fields = ["option"]
    permission_classes = [IsAuthenticated]


class FactionViewSet(ModelViewSet):
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer
    filterset_fields = ["game"]
    permission_classes = [IsAuthenticated]

class TieBreakerViewSet(ModelViewSet):
    queryset = TieBreaker.objects.all()
    serializer_class = TieBreakerSerializer
    filterset_fields = ["result_config"]
    permission_classes = [IsAuthenticated]


class ResultConfigViewSet(ModelViewSet):
    queryset = ResultConfig.objects.all()
    serializer_class = ResultConfigSerializer
    filterset_fields = ["game"]
    permission_classes = [IsAuthenticated]


class StartingPointSystemViewSet(ModelViewSet):
    queryset = StartingPointSystem.objects.all()
    serializer_class = StartingPointSystemSerializer
    permission_classes = [IsAuthenticated]


class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticated]


# Subqueries to count members/results without cross-join inflation that
# would occur when combining multiple Count() annotations on different
# multi-valued relations of SelectedGame.
_RESULT_COUNT_SQ = Subquery(
    Result.objects.filter(selected_game=OuterRef("pk"))
    .order_by()
    .values("selected_game")
    .annotate(c=Count("*"))
    .values("c"),
    output_field=IntegerField(),
)
_LEAGUE_MEMBER_COUNT_SQ = Subquery(
    League.members.through.objects.filter(league_id=OuterRef("league_id"))
    .order_by()
    .values("league_id")
    .annotate(c=Count("*"))
    .values("c"),
    output_field=IntegerField(),
)


class SelectedGameViewSet(ModelViewSet):
    queryset = (
        SelectedGame.objects.all()
        .select_related("game", "game__platform", "league", "profile")
        .prefetch_related(
            "selected_options__game_option",
            "selected_options__choice",
            "result_set",
        )
        .annotate(
            result_count=Coalesce(_RESULT_COUNT_SQ, 0),
            league_member_count=Coalesce(_LEAGUE_MEMBER_COUNT_SQ, 0),
        )
    )
    serializer_class = SelectedGameSerializer
    filterset_fields = ["league", "profile"]
    permission_classes = [IsAuthenticated]


class BanDecisionViewSet(ModelViewSet):
    queryset = BanDecision.objects.all()
    serializer_class = BanDecisionSerializer
    filterset_fields = ["league"]
    permission_classes = [IsAuthenticated]


class SelectedOptionViewSet(ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer
    permission_classes = [IsAuthenticated]


class FullGameViewSet(ModelViewSet):
    queryset = (
        Game.objects.all()
        .select_related("platform")
        .prefetch_related(
            "options__choices",
            "options__availability_groups__conditions__depends_on_option",
            "options__availability_groups__conditions__expected_choice",
        )
    )
    serializer_class = FullGameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        manage_only = (
                self.request.query_params.get("manage_only", "false").lower() == "true"
        )
        is_admin = self.request.user and self.request.user.is_staff

        if not (manage_only and is_admin):
            queryset = queryset.filter(selectable=True)

        return queryset
