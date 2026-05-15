from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from taskboard.models import Task
from taskboard.serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    """Admin-only Task Board CRUD endpoints."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAdminUser]
