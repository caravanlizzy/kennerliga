from rest_framework import serializers

from game.models import SelectedGame, BanDecision
from game.serializers import SelectedGameSerializer, GameSerializer
from season.models import Season, SeasonParticipant


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


class SeasonParticipantSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_name = serializers.SerializerMethodField()
    selected_game = serializers.SerializerMethodField()
    banned_game = serializers.SerializerMethodField()
    is_active_player = serializers.SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            'id',
            'username',
            'profile_name',
            'selected_game',
            'banned_game',
            'is_active_player',
            'rank',  # from the model
        ]

    def get_username(self, obj):
        return obj.profile.user.username  # Assuming PlayerProfile has a OneToOneField to User

    def get_profile_name(self, obj):
        return obj.profile.profile_name

    def get_selected_game(self, obj):
        league = self.context.get('league')
        if not league:
            return None
        selected_game = SelectedGame.objects.filter(player=obj.profile, league=league).first()
        return SelectedGameSerializer(selected_game).data if selected_game else None

    def get_banned_game(self, obj):
        league = self.context.get('league')
        if not league:
            return None
        ban_decision = BanDecision.objects.filter(player=obj.profile, league=league).first()
        return GameSerializer(ban_decision.game).data if ban_decision and ban_decision.game else None

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return obj == league.active_player if league else False

