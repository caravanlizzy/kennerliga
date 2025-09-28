import random
import secrets
import string

from rest_framework import status
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
    permission_classes = [IsAdminUser]   # or [IsAdminUser] if only admins may invite
    http_method_names = ["post", "delete", "get", "head", "options"]  # adjust as needed

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]

        # Block duplicate invites or existing users
        if User.objects.filter(username=username).exists():
            return Response({"detail": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if UserInvitation.objects.filter(username=username).exists():
            return Response({"detail": "Invitation already exists for this username."}, status=status.HTTP_400_BAD_REQUEST)

        invitation = UserInvitation.objects.create(
            username=username,
            otp=generate_otp(4),
            created_by=request.user  # requires a field on the model, optional
        )

        # Return only what you need. If OTP must be shown once, include it here.
        data = self.get_serializer(invitation).data
        data["otp"] = invitation.otp
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        invitation = self.get_object()
        invitation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


def generate_otp(length=4):
    # digits only to match your 4-digit flow; increase length if you can
    return ''.join(secrets.choice(string.digits) for _ in range(length))