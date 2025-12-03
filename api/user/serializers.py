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
        fields = '__all__'


class PlayerProfileSerializer(ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['id', 'username', 'profile_name']


class UserInviteLinkSerializer(serializers.ModelSerializer):
    invite_url = serializers.SerializerMethodField()

    class Meta:
        model = UserInviteLink
        fields = ["id", "key", "label", "created_by", "created_at", "expires_at", "invite_url"]
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
    class Meta:
        model = Feedback
        fields = ['message', 'user', 'datetime']
        read_only_fields = ['user', 'datetime']