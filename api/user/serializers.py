from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlencode
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from user.models import PlayerProfile, UserInviteLink, Feedback

User = get_user_model()


class UserSerializer(ModelSerializer):
    """
    Serializer for the User model.
    """
    profile_id = serializers.IntegerField(source="profile.id", read_only=True)
    win_rate = serializers.SerializerMethodField(read_only=True)
    avg_position = serializers.SerializerMethodField(read_only=True)
    most_participated_league_level = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_id",
            "win_rate",
            "avg_position",
            "most_participated_league_level",
        ]

    def _get_stats(self, obj):
        if not hasattr(obj, "_cached_summary_stats"):
            from user.service import get_user_summary_stats

            obj._cached_summary_stats = get_user_summary_stats(obj)
        return obj._cached_summary_stats

    def get_win_rate(self, obj):
        return self._get_stats(obj)["win_rate"]

    def get_avg_position(self, obj):
        return self._get_stats(obj)["avg_position"]

    def get_most_participated_league_level(self, obj):
        return self._get_stats(obj)["most_participated_league_level"]


class PlayerProfileSerializer(ModelSerializer):
    """
    Serializer for the PlayerProfile model.
    """
    class Meta:
        model = PlayerProfile
        fields = ["id", "user", "profile_name"]


class UserInviteLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserInviteLink model.
    Generates a full invite URL for the frontend.
    """
    invite_url = serializers.SerializerMethodField()
    player_profile_details = PlayerProfileSerializer(
        source="player_profile", read_only=True
    )

    class Meta:
        model = UserInviteLink
        fields = [
            "id",
            "key",
            "label",
            "player_profile",
            "player_profile_details",
            "created_by",
            "created_at",
            "expires_at",
            "invite_url",
        ]
        read_only_fields = ["id", "key", "created_by", "created_at", "invite_url"]

    def get_invite_url(self, obj):
        frontend_base = getattr(settings, "FRONTEND_REGISTER_URL", None)
        if frontend_base:
            query = urlencode({"key": obj.key})
            sep = "&" if "?" in frontend_base else "?"
            return f"{frontend_base}{sep}{query}"
        return None


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for handling user registration data, including the invite key.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    invite_key = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for the Feedback model.
    """
    username = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ["message", "user", "datetime", "username"]
        read_only_fields = ["user", "datetime", "username"]

    def get_username(self, obj):
        return obj.user.username
