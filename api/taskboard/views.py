from rest_framework.viewsets import ModelViewSet
from api.permissions import IsAdminOrReadOnly

from taskboard.models import Task
from taskboard.serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    """Task Board endpoints: read for all authenticated users, write for admins only."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAdminOrReadOnly]
