from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import PlatformPlayer


class LoginApiView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if both username and password are provided
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if authentication was successful
        if user is not None:
            # If authentication successful, return user data or token
            # For example, you can return user data or JWT token here
            # print(get_token(user))
            return Response({'message': 'Login successful', "user": get_user_information(user)},
                            status=status.HTTP_200_OK)
        else:
            # If authentication failed, return error message
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutApiView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        # Check if the user is authenticated
        token = request.auth  # The token is automatically attached to authenticated requests

        if token:
            # Find and delete the token to log the user out
            try:
                token_object = Token.objects.get(key=token)
                token_object.delete()
                return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No token provided or invalid token'}, status=status.HTTP_400_BAD_REQUEST)


def create_token(user):
    return Token.objects.create(user=user)


def has_token(user):
    return Token.objects.filter(user=user).exists()


def get_token(user):
    if has_token(user):
        token = Token.objects.get(user=user)
    else:
        token = create_token(user)
    return str(token)


def get_user_information(user):
    token = get_token(user)
    user = {
        "username": user.username,
        "token": token,
        "platform_players": get_platform_players(user)
    }
    return user


def get_platform_players(user):
    player_profile = user.profile
    platform_players = PlatformPlayer.objects.filter(player_profile=player_profile)
    platform_player_dict = {pp.platform.name: pp.name for pp in platform_players}
    return platform_player_dict
