from rest_framework.serializers import ModelSerializer

from release_note.models import ReleaseNote


class ReleaseNoteSerializer(ModelSerializer):
    class Meta:
        model = ReleaseNote
        fields = ["id", "title", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
