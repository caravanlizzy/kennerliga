from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class LoginApiView(APIView):
    def post(self, request, *args, **kwargs):
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
            print(get_token(user))
            return Response({'message': 'Login successful' , "user": get_user_information(user)}, status=status.HTTP_200_OK)
        else:
            # If authentication failed, return error message
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


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
        "id": user.id,
        "username": user.username,
        "bga_name": user.bga_name,
        "email": user.email,
        "token": token,
    }
    return user