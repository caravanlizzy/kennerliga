from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from league.models import League
from league.serializer import LeagueSerializer, LeagueDetailSerializer

class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

class LeagueDetailViewSet(ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueDetailSerializer
