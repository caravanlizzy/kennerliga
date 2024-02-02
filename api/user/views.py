from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from user.serializers import UserSerializer
from user.models import User

# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ IsAuthenticated ]
