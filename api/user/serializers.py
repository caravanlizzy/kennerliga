from rest_framework.serializers import ModelSerializer

from user.models import User, PlayerProfile


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PlayerProfileSerializer(ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['id', 'username', 'profile_name']

