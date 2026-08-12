from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from api.permissions import IsAdminOrReadOnly

from announcement.models import Announcement
from announcement.serializers import AnnouncementSerializer


class AnnouncementViewSet(ModelViewSet):
    """
    API viewset for viewing and editing announcements.
    Only active announcements (visible_until > now) are listed by default.
    """
    queryset = Announcement.objects.filter(visible_until__gt=timezone.now())
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]
