from rest_framework.serializers import ModelSerializer

from game.models import Faction


class FactionSerializer(ModelSerializer):
    """
    Serializer for the Faction model.
    """
    class Meta:
        model = Faction
        fields = "__all__"
