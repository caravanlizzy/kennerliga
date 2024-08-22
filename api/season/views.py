# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from kennerliga import Kennerliga
from user.models import PlayerProfile


class SeasonRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.headers.get('Authorization'))
        if not self.request.user:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            return HttpResponseNotFound("Player profile not found.")
        current_season = Kennerliga.get_current_season()
        current_season.participants.add(player_profile)
        current_season.save()
        return Response(f'Participant {player_profile.profile_name} has been added to the current season.')


