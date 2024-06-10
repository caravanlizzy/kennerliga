from rest_framework.serializers import ModelSerializer

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class GameOptionSerializer(ModelSerializer):
    class Meta:
        model = GameOption
        fields = '__all__'


class GameOptionChoiceSerializer(ModelSerializer):
    class Meta:
        model = GameOptionChoice
        fields = '__all__'


class FactionSerializer(ModelSerializer):
    class Meta:
        model = Faction
        fields = '__all__'


class TieBreakerSerializer(ModelSerializer):
    class Meta:
        model = TieBreaker
        fields = '__all__'


class ResultConfigSerializer(ModelSerializer):
    class Meta:
        model = ResultConfig
        fields = '__all__'


class StartingPointSystemSerializer(ModelSerializer):
    class Meta:
        model = StartingPointSystem
        fields = '__all__'


class PlatformSerializer(ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'


class SelectedGameSerializer(ModelSerializer):
    class Meta:
        model = SelectedGame
        fields = '__all__'


class SelectedOptionSerializer(ModelSerializer):
    class Meta:
        model = SelectedOption
        fields = '__all__'
