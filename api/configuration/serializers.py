from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from configuration.models import AppConfiguration


class AppConfigurationSerializer(ModelSerializer):
    """
    Serializer for a single app-wide configuration version. Read-only helper
    fields expose human-readable labels for the referenced game and author
    so the admin page can render history without extra lookups.
    """

    tie_decider_game_name = serializers.CharField(
        source="tie_decider_game.name", read_only=True, default=None
    )
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True, default=None
    )

    class Meta:
        model = AppConfiguration
        fields = [
            "id",
            "max_same_game_per_year",
            "tie_decider_game",
            "tie_decider_game_name",
            "created_at",
            "created_by",
            "created_by_username",
        ]
        read_only_fields = ["created_at", "created_by"]
