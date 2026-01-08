from rest_framework import serializers
from django.utils.html import escape

from chat.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'text', 'user', 'datetime', 'sender', 'label']
        read_only_fields = ['id', 'user', 'datetime', 'sender', 'label']

    @staticmethod
    def get_sender(obj):
        # Assuming that the 'user' field in the Chat model is a ForeignKey to a User model
        return obj.user.username if obj.user else None

    def validate_text(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Message text cannot be empty.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['text'] = escape(validated_data['text'])
        return super().create(validated_data)
