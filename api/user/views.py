from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from league.models import League
from league.serializer import LeagueSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer
from user.models import User, PlayerProfile, Platform, PlatformPlayer, UserInviteLink, Feedback
from user.serializers import UserSerializer, UserInviteLinkSerializer, UserRegistrationSerializer, \
    PlayerProfileSerializer, FeedbackSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lookup = self.kwargs["pk"]  # Django REST by default uses pk
        qs = self.get_queryset()
        # Try ID first, then username
        user = None
        if lookup.isdigit():
            user = qs.filter(id=lookup).first()
        if user is None:
            user = qs.filter(username=lookup).first()
        if not user:
            raise NotFound("User not found.")
        return user

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


class UserInviteLinkViewSet(ModelViewSet):
    """
    Admin-only:
      - GET    /invite-links/        list (includes invite_url)
      - POST   /invite-links/        create
      - GET    /invite-links/{id}/   retrieve
      - DELETE /invite-links/{id}/   destroy
    """
    queryset = UserInviteLink.objects.select_related("created_by").all()
    serializer_class = UserInviteLinkSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UserRegistrationViewSet(ViewSet):
    """
    Public:
      - POST /register/                 -> create user (consumes invite)
      - GET  /register/validate/?key=.. -> check invite validity
    """
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        invite_key = serializer.validated_data["invite_key"]

        try:
            with transaction.atomic():
                invite = UserInviteLink.objects.select_for_update().get(key=invite_key)

                if invite.is_expired():
                    invite.delete()
                    return Response({"detail": "Invite expired."}, status=400)

                user = User.objects.create_user(username=username, password=password)

                # Check if invite has an existing PlayerProfile
                if invite.player_profile:
                    # Link user to existing profile
                    player_profile = invite.player_profile
                    player_profile.user = user
                    player_profile.save()
                else:
                    # Create a new PlayerProfile
                    player_profile = PlayerProfile.objects.create(user=user, profile_name=username)

                    # Remove PlatformPlayer handling for now
                    # BGA = Platform.objects.get(name="BGA")
                    # PlatformPlayer.objects.create(
                    #     player_profile=player_profile,
                    #     platform=BGA,
                    #     name=user.username,
                    # )

                # Delete invite after success
                invite.delete()

            return Response({"detail": f"User {username} created successfully."}, status=201)

        except UserInviteLink.DoesNotExist:
            return Response({"detail": "Invalid invite key."}, status=400)
        except Platform.DoesNotExist:
            return Response({"detail": "Platform 'BGA' not configured."}, status=500)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    # @action(detail=False, methods=["get"], url_path="validate")
    # def validate_invite(self, request):
    #     raw_key = request.query_params.get("invite") or request.query_params.get("key")
    #     if not raw_key:
    #         return Response({"valid": False, "reason": "missing_key"}, status=400)
    #
    #     key_hash = _hash_key(raw_key)
    #
    #     try:
    #         invite = UserInviteLink.objects.get(key_hash=key_hash)
    #     except UserInviteLink.DoesNotExist:
    #         return Response({"valid": False, "reason": "not_found"}, status=404)
    #
    #     if invite.is_expired():
    #         invite.delete()
    #         return Response({"valid": False, "reason": "expired"}, status=410)
    #
    #     return Response({
    #         "valid": True,
    #         "label": invite.label,
    #         "expires_at": invite.expires_at,
    #     }, status=200)


class PlayerProfileViewSet(ModelViewSet):
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PlayerProfile.objects.all()

        # Check for user__isnull query parameter
        user_isnull = self.request.query_params.get('user__isnull', None)

        if user_isnull is not None:
            # Strip whitespace and slashes, then convert to lowercase
            user_isnull = user_isnull.strip().strip('/').lower()

            if user_isnull in ['true', '1', 'yes']:
                queryset = queryset.filter(user__isnull=True)
            elif user_isnull in ['false', '0', 'no']:
                queryset = queryset.filter(user__isnull=False)

        return queryset


class FeedbackViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    http_method_names = ["get", "post", "head", "options"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
