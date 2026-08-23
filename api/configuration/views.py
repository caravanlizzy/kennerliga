from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsAdminOrReadOnly
from configuration.models import AppConfiguration
from configuration.serializers import AppConfigurationSerializer


class AppConfigurationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    API viewset for the app-wide configuration.

    Configurations are versioned: creating one adds a new immutable row
    (keeping the full history), and there is intentionally no update/delete.
    ``list`` returns the change history (newest first); ``current`` returns
    the active configuration. Everyone authenticated can read; only admins
    can create a new version.
    """

    queryset = AppConfiguration.objects.select_related(
        "tie_decider_game", "created_by"
    ).all()
    serializer_class = AppConfigurationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Returns the active (most recent) configuration, or ``null`` if the
        app has never been configured."""
        config = AppConfiguration.current()
        if config is None:
            return Response(None)
        return Response(self.get_serializer(config).data)
