from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer, FactionSerializer, \
    TieBreakerSerializer, ResultConfigSerializer, StartingPointSystemSerializer, PlatformSerializer, \
    SelectedGameSerializer, SelectedOptionSerializer, FullGameSerializer


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

# Not required since FullGameViewSet covers all of this automatically
# class GameDetailsViewSet(ModelViewSet):
#     queryset = Game.objects.all()
#     serializer_class = GameSerializer
#     permission_classes = [IsAuthenticated]
#
#     def retrieve(self, request, *args, **kwargs):
#         # Get the specific Game instances
#         game = self.get_object()
#
#         # Serialize the main game data
#         game_data = GameSerializer(game).data
#
#         # Serialize related GameOptions and their choices
#         options_data = []
#         for option in game.options.all():
#             option_data = GameOptionSerializer(option).data
#             choices_data = GameOptionChoiceSerializer(option.choices.all(), many=True).data
#             option_data['choices'] = choices_data  # Add choices data to each option
#             options_data.append(option_data)
#
#         # Add the options with choices to the main game data
#         game_data['options'] = options_data
#         print(game_data)
#         return Response(game_data, status=status.HTTP_200_OK)


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
    filterset_fields = ['league']

    def perform_create(self, serializer):
        selected_game = serializer.save()

        # Post-save logic:
        league = selected_game.league

        league.next_player()
        league.check_state()


class SelectedOptionViewSet(ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer


class FullGameViewSet(ModelViewSet):
    queryset = Game.objects.all().prefetch_related('options__choices')
    serializer_class = FullGameSerializer
    permission_classes = [IsAuthenticated]
