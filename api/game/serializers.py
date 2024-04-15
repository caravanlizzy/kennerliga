from rest_framework.serializers import ModelSerializer
from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker

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
