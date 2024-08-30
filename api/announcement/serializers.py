from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from announcement.models import Announcement


class AnnouncementSerializer(ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
