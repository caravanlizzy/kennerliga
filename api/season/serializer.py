from rest_framework import serializers

from season.models import Season


class SeasonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    season_start_time = serializers.SerializerMethodField(read_only=True)
    time_to_start = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_name(obj):
        return obj.name

    @staticmethod
    def get_season_start_time(obj):
        return obj.season_start_time

    @staticmethod
    def get_time_to_start(obj):
        # Returning as a human-readable string or as total seconds
        return str(obj.time_to_start)  # or obj.time_to_start.total_seconds()

    class Meta:
        model = Season
        fields = '__all__'
