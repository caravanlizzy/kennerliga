from rest_framework.serializers import ModelSerializer

from taskboard.models import Task


class TaskSerializer(ModelSerializer):
    """
    Serializer for the Task model.
    """
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
