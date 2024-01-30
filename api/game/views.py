from rest_framework.viewsets import ModelViewSet
from game.serializers import GameSerializer
from game.models import Game

class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
