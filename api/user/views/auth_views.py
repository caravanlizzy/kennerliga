import logging

logger = logging.getLogger(__name__)

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from user.models import PlayerProfile, User, UserInviteLink
from user.serializers import (
    PasswordResetConfirmSerializer,
    UserInviteLinkSerializer,
    UserRegistrationSerializer,
)


class UserInviteLinkViewSet(ModelViewSet):
    """
    API viewset for managing user invite links and password restoration links.
    Restricted to admin users.
    """
    queryset = UserInviteLink.objects.select_related(
        "created_by", "user", "player_profile"
    ).all()
    serializer_class = UserInviteLinkSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        link_type = serializer.validated_data.get(
            "type", UserInviteLink.TYPE_INVITATION
        )
        if link_type == UserInviteLink.TYPE_PASSWORD and user:
            UserInviteLink.objects.filter(
                user=user, type=UserInviteLink.TYPE_PASSWORD
            ).delete()
            if not serializer.validated_data.get("label"):
                serializer.validated_data["label"] = (
                    f"Password reset for {user.username}"
                )
        serializer.save(created_by=self.request.user)


class UserRegistrationViewSet(ViewSet):
    """
    API viewset for public user registration using an invite link.
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
                invite = UserInviteLink.objects.select_for_update().get(
                    key=invite_key, type=UserInviteLink.TYPE_INVITATION
                )

                if invite.is_expired():
                    invite.delete()
                    return Response({"detail": "Invite expired."}, status=400)

                user = User.objects.create_user(
                    username=username, password=password
                )

                # Check if invite has an existing PlayerProfile
                if invite.player_profile:
                    # Link user to existing profile
                    player_profile = invite.player_profile
                    player_profile.user = user
                    player_profile.save()
                else:
                    # Create a new PlayerProfile
                    PlayerProfile.objects.create(
                        user=user, profile_name=username
                    )

                # Delete invite after success
                invite.delete()

            return Response(
                {"detail": f"User {username} created successfully."}, status=201
            )

        except UserInviteLink.DoesNotExist:
            return Response({"detail": "Invalid invite key."}, status=400)
        except Exception as e:
            logger.exception("User registration failed.")
            return Response({"detail": str(e)}, status=400)


class UserPasswordResetViewSet(ViewSet):
    """
    API viewset for confirming password resets using one-time token keys.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="confirm")
    def confirm(self, request):
        """
        Set a new password using the one-time token key.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key = serializer.validated_data["key"].strip()
        password = serializer.validated_data["password"]

        try:
            with transaction.atomic():
                reset_link = UserInviteLink.objects.select_for_update().get(
                    key=key, type=UserInviteLink.TYPE_PASSWORD
                )

                if reset_link.is_expired():
                    reset_link.delete()
                    return Response(
                        {"detail": "Reset link expired."}, status=400
                    )

                user = reset_link.user
                if not user:
                    reset_link.delete()
                    return Response(
                        {"detail": "Invalid reset link."}, status=400
                    )

                user.set_password(password)
                user.save()

                reset_link.delete()

            return Response(
                {"detail": "Password has been reset successfully."},
                status=200,
            )
        except UserInviteLink.DoesNotExist:
            return Response({"detail": "Invalid reset key."}, status=400)
        except Exception as e:
            logger.exception("Password reset failed.")
            return Response({"detail": str(e)}, status=400)
