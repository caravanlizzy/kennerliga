from django.utils import timezone
from rest_framework.viewsets import ModelViewSet

from organisation.models import Announcement
from organisation.serializers import AnnouncementSerializer


class AnnouncementViewSet(ModelViewSet):
    queryset = Announcement.objects.filter(visible_until__gt=timezone.now())
    serializer_class = AnnouncementSerializer
    authentication_classes = []
