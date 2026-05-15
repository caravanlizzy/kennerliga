from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from taskboard.models import Task
from taskboard.serializers import TaskSerializer


class IsAdminOrReadOnly(BasePermission):
    """Authenticated users can read; only admins (staff) can write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_staff)


class TaskViewSet(ModelViewSet):
    """Task Board endpoints: read for all authenticated users, write for admins only."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
