from rest_framework.serializers import ModelSerializer

from announcement.models import Announcement


class AnnouncementSerializer(ModelSerializer):
    """
    Serializer for the Announcement model.
    """
    class Meta:
        model = Announcement
        fields = "__all__"
