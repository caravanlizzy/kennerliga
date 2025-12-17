from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat
from chat.serializer import ChatSerializer


class ChatViewSet(ModelViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        limit = self.request.query_params.get('limit', None)
        last_datetime = self.request.query_params.get('last_datetime')

        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValidationError('Limit must be a positive integer.')
            except ValueError:
                raise ValidationError('Limit must be an integer.')
        else:
            limit = 20  # Default limit if no limit is specified

        chat_queryset = Chat.objects.all()
        if last_datetime is not None:
            parsed_last_datetime = parse_datetime(last_datetime)
            chat_queryset = chat_queryset.filter(datetime__gt=parsed_last_datetime)

        # Order by the DateTimeField in descending order to get the most recent items first
        return chat_queryset.order_by('-datetime')[:limit]

    serializer_class = ChatSerializer
