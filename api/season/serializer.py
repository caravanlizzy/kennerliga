from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, BooleanField, CharField
from rest_framework.serializers import ModelSerializer

from game.serializers import SelectedGameSerializer
from season.models import Season, SeasonParticipant
from season.participant_prefetch import get_league_standings_order
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
        return obj.is_completed

    def get_is_incomplete(self, obj):
        is_empty = self.get_is_empty(obj)
        if is_empty:
            return False
        return not self.get_is_completed(obj)

    class Meta:
        model = Season
        fields = "__all__"


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
    username = CharField(source="profile.user.username", read_only=True)
    profile_name = CharField(source="profile.profile_name", read_only=True)
    season_details = SeasonSerializer(source="season", read_only=True)
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
    league_position = SerializerMethodField()
    # Extra marker to indicate entries coming from previous season and not yet registered
    # Existing clients can ignore it; defaults to False for real participants
    is_prev_unregistered = serializers.BooleanField(read_only=True, default=False)
    league = SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            "id",
            "season",
            "profile",
            "rank",  # write
            "username",
            "profile_name",
            "season_details",
            "selected_games",  # read
            "has_banned",
            "is_active_player",
            "is_prev_unregistered",
            "my_banned_game",
            "league_position",
            "league",
        ]

    # ---- context / prefetch helpers ----------------------------------------
    def _league(self):
        """League this participant is being rendered in (from context)."""
        return self.context.get("league")

    @staticmethod
    def _profile_selected_games(obj, league):
        """
        Return SelectedGames for ``obj.profile`` in ``league`` using the
        ``profile.sg_in_league`` prefetched attribute when available.
        Falls back to a filtered query only if the prefetch is missing.
        """
        prefetched = getattr(obj.profile, "sg_in_league", None)
        if prefetched is not None:
            return prefetched
        # Fallback (no prefetch attached) - kept for safety, not for hot paths.
        from game.models import SelectedGame

        return list(
            SelectedGame.objects.filter(profile=obj.profile, league=league)
            .select_related("game")
            .order_by("id")
        )

    @staticmethod
    def _profile_bans(obj, league):
        """Same idea for BanDecisions made by this profile in the league."""
        prefetched = getattr(obj.profile, "bans_in_league", None)
        if prefetched is not None:
            return prefetched
        from game.models import BanDecision

        return list(
            BanDecision.objects.filter(
                league=league, player_banning=obj.profile
            ).select_related("selected_game__game")
        )

    # ---- field getters -----------------------------------------------------
    def get_league(self, obj):
        league = self._league()
        if not league:
            return None
        return {"id": league.id, "level": league.level}

    def get_league_position(self, obj):
        league = self._league()
        if not league:
            return None
        standings_order = get_league_standings_order(league)
        try:
            return standings_order.index(obj.profile_id) + 1
        except ValueError:
            return None

    def get_my_banned_game(self, obj):
        league = self._league()
        if not league:
            return None

        bans = self._profile_bans(obj, league)
        selected_game = next(
            (b.selected_game for b in bans if b.selected_game_id), None
        )
        if not selected_game:
            return None

        return SelectedGameSerializer(selected_game, context=self.context).data

    def get_selected_games(self, obj):
        league = self._league()
        if not league:
            return []
        return SelectedGameSerializer(
            self._profile_selected_games(obj, league),
            many=True,
            context=self.context,
        ).data

    def get_is_active_player(self, obj):
        league = self._league()
        if not league:
            return False
        # Prefer cached active_player_id (attached by attach_league_lookups)
        active_id = getattr(league, "_active_player_id", None)
        if active_id is None:
            active_id = league.active_player_id
        return obj.id == active_id
