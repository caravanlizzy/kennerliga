from rest_framework.viewsets import ModelViewSet
from user.serializers import UserSerializer
from user.models import User

# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
