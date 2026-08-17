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
    total_games = serializers.SerializerMethodField(read_only=True)
    win_rate = serializers.SerializerMethodField(read_only=True)
    avg_position = serializers.SerializerMethodField(read_only=True)
    most_participated_league_level = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_id",
            "total_games",
            "win_rate",
            "avg_position",
            "most_participated_league_level",
        ]

    def _get_stats(self, obj):
        request = self.context.get("request") if hasattr(self, "context") and self.context else None
        exclude_2p_only = False
        exclude_3p_only = False
        player_count = None
        years = None

        if request and hasattr(request, "query_params"):
            exclude_2p_only = request.query_params.get("exclude_2p_only", "").lower() in ["true", "1"]
            exclude_3p_only = request.query_params.get("exclude_3p_only", "").lower() in ["true", "1"]
            player_count = request.query_params.get("player_count")
            if player_count and player_count.lower() == "all":
                player_count = None

            raw_years = request.query_params.getlist("years") + request.query_params.getlist("years[]")
            if not raw_years and "years" in request.query_params:
                raw_years = [request.query_params.get("years")]
            if not raw_years and "years[]" in request.query_params:
                raw_years = [request.query_params.get("years[]")]

            parsed_years = []
            for item in raw_years:
                if isinstance(item, str) and "," in item:
                    for part in item.split(","):
                        if part.strip().isdigit():
                            parsed_years.append(int(part.strip()))
                elif str(item).isdigit():
                    parsed_years.append(int(item))
            years = tuple(sorted(list(set(parsed_years)))) if parsed_years else None

        cache_key = (exclude_2p_only, exclude_3p_only, player_count, years)
        if not hasattr(obj, "_cached_summary_stats"):
            obj._cached_summary_stats = {}
        if cache_key not in obj._cached_summary_stats:
            from user.service import get_user_summary_stats

            obj._cached_summary_stats[cache_key] = get_user_summary_stats(
                obj,
                exclude_2p_only=exclude_2p_only,
                exclude_3p_only=exclude_3p_only,
                player_count=player_count,
                years=years,
            )
        return obj._cached_summary_stats[cache_key]

    def get_total_games(self, obj):
        return self._get_stats(obj).get("total_games", 0)

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
