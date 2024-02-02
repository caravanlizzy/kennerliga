from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from game.serializers import GameSerializer
from game.models import Game

class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [ IsAuthenticated ]
