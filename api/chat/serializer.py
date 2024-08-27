from rest_framework import serializers

from chat.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chat
        fields = ['text', 'user', 'datetime', 'sender']
        read_only_fields = ['user', 'datetime', 'sender']

    def get_sender(self, obj):
        # Assuming that the 'user' field in the Chat model is a ForeignKey to a User model
        return obj.user.username if obj.user else None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
