from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlencode
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from user.models import PlayerProfile, UserInviteLink, Feedback

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class PlayerProfileSerializer(ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['id', 'user', 'profile_name']


class UserInviteLinkSerializer(serializers.ModelSerializer):
    invite_url = serializers.SerializerMethodField()
    player_profile_details = PlayerProfileSerializer(source='player_profile', read_only=True)

    class Meta:
        model = UserInviteLink
        fields = ["id", "key", "label", "player_profile", "player_profile_details", "created_by", "created_at", "expires_at", "invite_url"]
        read_only_fields = ["id", "key", "created_by", "created_at", "invite_url"]

    def get_invite_url(self, obj):
        frontend_base = getattr(settings, "FRONTEND_REGISTER_URL", None)
        if frontend_base:
            query = urlencode({"key": obj.key})
            sep = "&" if "?" in frontend_base else "?"
            return f"{frontend_base}{sep}{query}"
        return None


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    invite_key = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['message', 'user', 'datetime', 'username']
        read_only_fields = ['user', 'datetime', 'username']

    def get_username(self, obj):
        return obj.user.username