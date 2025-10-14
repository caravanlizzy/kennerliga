from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from league.models import League
from league.serializer import LeagueSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season, SeasonParticipant
from season.serializer import SeasonSerializer
from user.models import User, PlayerProfile, Platform, PlatformPlayer, _hash_key, UserInviteLink
from user.serializers import UserSerializer, UserInviteLinkSerializer, UserRegistrationSerializer, \
    PlayerProfileSerializer


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


class UserInviteLinkViewSet(ModelViewSet):
    """
    Admin-only:
      - GET    /invite-links/        list
      - POST   /invite-links/        create (returns raw invite_key once)
      - GET    /invite-links/{id}/   retrieve
      - DELETE /invite-links/{id}/   destroy
    """
    queryset = UserInviteLink.objects.select_related("created_by").all()
    serializer_class = UserInviteLinkSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        label = ser.validated_data.get("label", "")
        expires_at = ser.validated_data.get("expires_at")

        invite, raw_key = UserInviteLink.create_with_random_key(
            created_by=request.user,
            label=label,
            expires_at=expires_at,
        )

        frontend_base = getattr(settings, "FRONTEND_REGISTER_URL", None)
        invite_url = None
        if frontend_base:
            query = urlencode({"key": raw_key})
            sep = "&" if "?" in frontend_base else "?"
            invite_url = f"{frontend_base}{sep}{query}"

        data = self.get_serializer(invite).data
        data.update({"invite_key": raw_key, "invite_url": invite_url})
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



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

        key_hash = _hash_key(invite_key)

        try:
            with transaction.atomic():
                invite = UserInviteLink.objects.select_for_update().get(key_hash=key_hash)

                if invite.is_expired():
                    invite.delete()
                    return Response({"detail": "Invite expired."}, status=400)

                # Create user + related models
                user = User.objects.create_user(username=username, password=password)

                profile_name = f"{username}_profile"
                player_profile = PlayerProfile.objects.create(user=user, profile_name=profile_name)

                BGA = Platform.objects.get(name="BGA")
                PlatformPlayer.objects.create(
                    player_profile=player_profile,
                    platform=BGA,
                    name=user.username,
                )

                # Delete invite after success
                invite.delete()

            return Response({"detail": f"User {username} created successfully."}, status=201)

        except UserInviteLink.DoesNotExist:
            return Response({"detail": "Invalid invite key."}, status=400)
        except Platform.DoesNotExist:
            return Response({"detail": "Platform 'BGA' not configured."}, status=500)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="validate")
    def validate_invite(self, request):
        raw_key = request.query_params.get("invite") or request.query_params.get("key")
        if not raw_key:
            return Response({"valid": False, "reason": "missing_key"}, status=400)

        key_hash = _hash_key(raw_key)

        try:
            invite = UserInviteLink.objects.get(key_hash=key_hash)
        except UserInviteLink.DoesNotExist:
            return Response({"valid": False, "reason": "not_found"}, status=404)

        if invite.is_expired():
            invite.delete()
            return Response({"valid": False, "reason": "expired"}, status=410)

        return Response({
            "valid": True,
            "label": invite.label,
            "expires_at": invite.expires_at,
        }, status=200)


class PlayerProfileViewSet(ModelViewSet):
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]