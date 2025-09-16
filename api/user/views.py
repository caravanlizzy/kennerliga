import random

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from league.models import League
from league.serializer import LeagueSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer
from user.models import User, UserInvitation, PlayerProfile, Platform, PlatformPlayer
from user.serializers import UserSerializer, UserInvitationSerializer


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


class UserInvitationViewSet(ModelViewSet):
    queryset = UserInvitation.objects.all()
    serializer_class = UserInvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'detail': 'Username is required.'}, status=400)
        otp = str(random.randint(1000, 9999))
        UserInvitation.objects.create(username=username, otp=otp)
        return Response({'otp': otp})

    def destroy(self, request, pk=None):
        invitation = self.get_object()
        invitation.delete()
        return Response({'detail': 'Invitation deleted.'})


class UserRegistrationViewSet(ViewSet):
    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        input_otp = request.data.get('otp')
        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=400)
        try:
            user_invitation = UserInvitation.objects.get(username=username)
            if user_invitation.failed_attempts > 3:
                return Response({'detail': 'Maximum number of failed attempts reached.'}, status=400)
            if input_otp != user_invitation.otp:
                user_invitation.failed_attempts += 1
                user_invitation.save()
                return Response({'detail': 'Invalid One Time Password.'}, status=400)
            user = User.objects.create_user(username=username, password=password)
            profile_name = username + '_profile'
            player_profile = PlayerProfile.objects.create(user=user, profile_name=profile_name)
            BGA = Platform.objects.get(name='BGA')
            PlatformPlayer.objects.create(
                player_profile=player_profile,
                platform=BGA,
                name=player_profile.user.username if player_profile.user else player_profile.profile_name
            )

            user_invitation.delete()
            return Response({f'detail': f'User {username} created successfully.'}, status=201)

        except Exception as e:
            return Response({'detail': str(e)}, status=400)
