# Create your views here.
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from league.models import League
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season
from season.service import get_running_season
from user.models import PlayerProfile


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally filter queryset based on the authenticated user's profile or other criteria
        return self.queryset.filter(player_profile__user=self.request.user)

    def perform_create(self, serializer):
        # Get the authenticated user's player profile
        try:
            player_profile = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            raise NotFound("Player profile not found for the authenticated user.")

        # Fetch the current running season and league
        try:
            season = get_running_season()
            league = League.objects.get(seasons=season)
        except Season.DoesNotExist:
            raise NotFound("Running season not found.")
        except League.DoesNotExist:
            raise NotFound("League for the current season not found.")

        # Save the Result instance with the additional context
        serializer.save(player_profile=player_profile, season=season, league=league)
