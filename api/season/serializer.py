from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, BooleanField, CharField
from rest_framework.serializers import ModelSerializer

from game.models import SelectedGame, BanDecision
from game.serializers import SelectedGameSerializer
from season.models import Season, SeasonParticipant
from user.models import PlayerProfile


class TLiveEventSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    leagueLevel = serializers.IntegerField(required=False, allow_null=True)
    leagueId = serializers.IntegerField(required=False, allow_null=True)
    data = serializers.DictField()


class SeasonSerializer(ModelSerializer):
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


class SeasonParticipantMiniSerializer(ModelSerializer):
    profile_name = CharField(source="profile.profile_name", read_only=True)
    username = SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = ("id", "profile_name", "username")
        read_only_fields = ("id", "profile_name", "username")

    def get_username(self, obj):
        user = getattr(obj.profile, "user", None)
        return getattr(user, "username", None)


class SeasonParticipantSerializer(ModelSerializer):
    username = CharField(source='profile.user.username', read_only=True)
    profile_name = CharField(source='profile.profile_name', read_only=True)
    season_details = SeasonSerializer(source='season', read_only=True)
    profile = serializers.PrimaryKeyRelatedField(
        queryset=PlayerProfile.objects.all(),
        required=True,
    )
    season = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        required=True,
    )
    selected_games = SerializerMethodField()
    my_banned_game = SerializerMethodField()
    has_banned = BooleanField(read_only=True)
    is_active_player = SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            'id', 'season', 'profile', 'rank',  # write
            'username', 'profile_name', 'season_details',
            'selected_games',  # read
            'has_banned', 'is_active_player',
            'my_banned_game',
        ]

    def get_my_banned_game(self, obj):
        league = self.context.get('league')
        if not league:
            return None

        ban_decision = BanDecision.objects.filter(
            league=league,
            player_banning=obj.profile
        ).select_related('selected_game').first()

        if not ban_decision or not ban_decision.selected_game:
            return None

        return SelectedGameSerializer(ban_decision.selected_game, context=self.context).data

    # ---- public getters -----------------------------------------------------
    def get_selected_games(self, obj):
        league = self.context.get('league')
        if not league:
            return []

        qs = (
            SelectedGame.objects
            .filter(profile=obj.profile, league=league)
            .select_related('game')
            .order_by('id')
        )

        return SelectedGameSerializer(qs, many=True, context=self.context).data

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return bool(league and obj == league.active_player)

