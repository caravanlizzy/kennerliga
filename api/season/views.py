# Create your views here.
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from manager.season_manager import SeasonManager
from season.models import Season
from season.serializer import SeasonSerializer
from user.models import PlayerProfile


class SeasonRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        if not self.request.user:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            return HttpResponseNotFound("Player profile not found.")
        current_season = SeasonManager.get_current_season()
        if not player_profile in current_season.participants.all():
            current_season.participants.add(player_profile)
            current_season.save()
            return Response(f'Participant {player_profile.profile_name} has been added to the current season.')
        return Response(f'Player {player_profile.profile_name} is already registered')


class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
