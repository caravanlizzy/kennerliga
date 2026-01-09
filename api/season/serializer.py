from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, BooleanField, CharField
from rest_framework.serializers import ModelSerializer

from game.models import SelectedGame, BanDecision
from game.serializers import SelectedGameSerializer
from league.models import League
from result.models import Result
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

    is_completed = serializers.SerializerMethodField(read_only=True)
    is_empty = serializers.SerializerMethodField(read_only=True)
    is_incomplete = serializers.SerializerMethodField(read_only=True)

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

    def get_is_empty(self, obj):
        # A season is empty if it has no participants
        return not obj.participants.exists()

    def get_is_completed(self, obj):
        # Optimized version
        leagues = obj.leagues.all()
        if not leagues.exists():
            return False
            
        participants = obj.participants.all()
        if not participants.exists():
            return False

        # If there are participants not assigned to any league, it's not completed?
        # Actually, in this app, participants are assigned to leagues.
        # Let's check if all participants belong to a league in this season.
        # But for status "is_completed", we care about the games in the leagues.

        # A season is completed if:
        # 1. All leagues in the season are status DONE.
        if leagues.filter(~Q(status='DONE')).exists():
            return False
            
        # 2. At least one league exists and has members.
        # (Already checked above)
        
        return True

    def get_is_incomplete(self, obj):
        is_empty = self.get_is_empty(obj)
        if is_empty:
            return False
        return not self.get_is_completed(obj)

    class Meta:
        model = Season
        fields = '__all__'


class SeasonWithLeaguesSerializer(SeasonSerializer):
    leagues = SerializerMethodField()

    def get_leagues(self, obj):
        from league.serializer import LeagueSerializer
        return LeagueSerializer(obj.leagues.all(), many=True).data


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

