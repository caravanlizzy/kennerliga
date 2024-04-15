from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from game.serializers import GameSerializer, GameOptionSerializer, GameOptionChoiceSerializer, FactionSerializer, TieBreakerSerializer
from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker

class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    # permission_classes = [ IsAuthenticated ]


class GameOptionViewSet(ModelViewSet):
    queryset = GameOption.objects.all()
    serializer_class = GameOptionSerializer
    filterset_fields = ['game']
    # permission_classes = [ IsAuthenticated ]


class GameOptionChoiceViewSet(ModelViewSet):
    queryset = GameOptionChoice.objects.all()
    serializer_class = GameOptionChoiceSerializer
    filterset_fields = ['option']
    # permission_classes = [ IsAuthenticated ]


class FactionViewSet(ModelViewSet):
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer
    filterset_fields = ['game']


class TieBreakerViewSet(ModelViewSet):
    queryset = TieBreaker.objects.all()
    serializer_class = TieBreakerSerializer
    filterset_fields = ['game']
