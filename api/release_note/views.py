from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from release_note.models import ReleaseNote
from release_note.serializers import ReleaseNoteSerializer


class ReleaseNoteViewSet(ModelViewSet):
    """
    list/retrieve: any authenticated (or anonymous) user can read release notes.
    create/update/destroy: admin users only.
    """

    queryset = ReleaseNote.objects.all().order_by("-created_at")
    serializer_class = ReleaseNoteSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]
