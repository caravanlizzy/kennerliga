from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from user.models import User, PlayerProfile, UserInvitation


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PlayerProfileSerializer(ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['id', 'username', 'profile_name']


class UserInvitationSerializer(ModelSerializer):
    class Meta:
        model = UserInvitation
        fields = '__all__'


class UserRegistrationSerializer(Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    otp = serializers.CharField(required=True)
