from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer, FactionSerializer, \
    TieBreakerSerializer, ResultConfigSerializer, StartingPointSystemSerializer, PlatformSerializer, \
    SelectedGameSerializer, SelectedOptionSerializer


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]


class GameDetailsViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Get the specific Game instance
        game = self.get_object()
        print(game)

        # Serialize the main game data
        game_data = GameSerializer(game).data

        # Serialize related GameOptions and their choices
        options_data = []
        for option in game.options.all():
            option_data = GameOptionSerializer(option).data
            choices_data = GameOptionChoiceSerializer(option.choices.all(), many=True).data
            option_data['choices'] = choices_data  # Add choices data to each option
            options_data.append(option_data)

        # Add the options with choices to the main game data
        game_data['options'] = options_data

        return Response(game_data, status=status.HTTP_200_OK)


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


class SelectedOptionViewSet(ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer
