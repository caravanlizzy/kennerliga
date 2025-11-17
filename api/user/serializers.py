from django.contrib.auth import get_user_model
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
    class Meta:
        model = UserInviteLink
        fields = ["id", "label", "created_by", "created_at", "expires_at"]
        read_only_fields = ["id", "created_by", "created_at"]


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