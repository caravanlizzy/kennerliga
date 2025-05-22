from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from league.models import League
from league.serializer import LeagueSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer
from user.models import User
from user.serializers import UserSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='leagues')
    def user_leagues(self, request, pk=None):
        """
        Custom action to return the leagues for a specific user.
        """
        user = self.get_object()  # Fetch the user by the ID from the URL (pk)
        leagues = League.objects.filter(members=user.profile)
        serializer = LeagueSerializer(leagues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='seasons')
    def user_seasons(self, request, pk=None):
        """
        Custom action to return the leagues for a specific user.
        """
        user = self.get_object()  # Fetch the user by the ID from the URL (pk)
        season = Season.objects.filter(participants=user.profile)
        serializer = SeasonSerializer(season, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='results')
    def user_results(self, request, pk=None):
        """
        Custom action to return the leagues for a specific user.
        """
        user = self.get_object()  # Fetch the user by the ID from the URL (pk)
        results = Result.objects.filter(player_profile=user.profile)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)




class MeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='current-league')
    def current_league(self, request):
        profile = request.user.profile

        participant = (
            SeasonParticipant.objects
            .filter(profile=profile, season__status=Season.SeasonStatus.RUNNING)
            .select_related('season')
            .first()
        )

        if not participant:
            return Response({'detail': 'No running season participation found.'}, status=404)

        league = League.objects.filter(
            members=participant,
            season=participant.season
        ).first()

        if not league:
            return Response({'detail': 'No league found for current season.'}, status=404)

        return Response(LeagueSerializer(league).data)

    @action(detail=False, methods=['get'], url_path='results')
    def results(self, request):
        results = Result.objects.filter(player_profile=request.user.profile)
        return Response(ResultSerializer(results, many=True).data)