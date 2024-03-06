from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer
from game.models import Game, GameOption, GameOptionChoice

class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    # permission_classes = [ IsAuthenticated ]


class GameOptionViewSet(ModelViewSet):
    queryset = GameOption.objects.all()
    serializer_class = GameOptionSerializer
    # permission_classes = [ IsAuthenticated ]


class GameOptionChoiceViewSet(ModelViewSet):
    queryset = GameOptionChoice.objects.all()
    serializer_class = GameOptionChoiceSerializer
    # permission_classes = [ IsAuthenticated ]
