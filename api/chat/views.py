from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat
from chat.serializer import ChatSerializer


class ChatViewSet(ModelViewSet):
    def get_queryset(self):
        limit = self.request.query_params.get('limit', None)

        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValidationError('Limit must be a positive integer.')
            except ValueError:
                raise ValidationError('Limit must be an integer.')
        else:
            limit = 10  # Default limit if no limit is specified

        # Order by the DateTimeField in descending order to get the most recent items first
        return Chat.objects.all().order_by('-datetime')[:limit]

    serializer_class = ChatSerializer
