from rest_framework.viewsets import ModelViewSet

from league.models import League

from league.serializer import LeagueSerializer


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
