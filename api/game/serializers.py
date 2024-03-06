from rest_framework.serializers import ModelSerializer
from game.models import Game, GameOption, GameOptionChoice

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
