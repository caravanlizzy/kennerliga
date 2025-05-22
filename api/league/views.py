from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from league.models import League
from league.serializer import LeagueSerializer, LeagueDetailSerializer
from rest_framework.views import APIView, Response, status
from league.service import rotate_active_player
from django.shortcuts import get_object_or_404

class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

class LeagueDetailViewSet(ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueDetailSerializer
