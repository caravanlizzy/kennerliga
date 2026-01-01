from django.db.models import OuterRef, Exists
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
    first_game_selection_banned_by_others = SerializerMethodField()
    my_banned_game = SerializerMethodField()
    has_banned = BooleanField(read_only=True)
    is_active_player = SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            'id', 'season', 'profile', 'rank',  # write
            'username', 'profile_name', 'season_details',
            'selected_games',  # read
            'first_game_selection_banned_by_others', 'has_banned', 'is_active_player',
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

    # ---- internal helper & cache -------------------------------------------
    def _league_member_count(self):
        """
        Cached member count for the league in context.
        """
        if hasattr(self, "_cached_league_member_count"):
            return self._cached_league_member_count

        league = self.context.get("league")
        self._cached_league_member_count = league.members.count() if league else 0
        return self._cached_league_member_count

    def _resolve_games_for_participant(self, obj):
        """
        For 3+ member leagues:
            returns (selected_sg, banned_sg)

        For 2 member leagues:
            returns (selected_sg, selected_two_sg, banned_sg)

        NOTE:
        "Banned-by-others" means "successfully banned":
            - 2 players: 1 BanDecision by the other player
            - 3+ players: 2 BanDecisions by other players
        """
        # Per-serializer cache so both getters don't redo work
        cache = getattr(self, '_sg_cache', None)
        if cache is None:
            cache = self._sg_cache = {}

        league = self.context.get('league')
        member_count = self._league_member_count()

        key = (obj.pk, member_count)
        if key in cache:
            return cache[key]

        if not league:
            cache[key] = (None, None) if member_count != 2 else (None, None, None)
            return cache[key]

        qs = SelectedGame.objects.filter(profile=obj.profile, league=league)

        count = qs.count()
        if count == 0:
            cache[key] = (None, None) if member_count != 2 else (None, None, None)
            return cache[key]

        successful_ban_threshold = 1 if member_count == 2 else 2

        from django.db.models import Count, Q  # local import to keep file-level imports minimal
        annotated = (qs
                     .annotate(
            bans_by_others_count=Count(
                "bandecision",
                filter=Q(
                    bandecision__league=league,
                    bandecision__player_banning__isnull=False,
                ) & ~Q(bandecision__player_banning=obj.profile),
                distinct=True,
            )
        )
                     .annotate(
            has_successful_ban_by_others=Q(bans_by_others_count__gte=successful_ban_threshold)
        )
                     .select_related('game')
                     .order_by('id'))

        if count == 1:
            sg = annotated.first()

            # If the only pick is successfully banned-by-others, it must not be returned as selected_game.
            if sg and getattr(sg, "has_successful_ban_by_others", False):
                if member_count == 2:
                    cache[key] = (None, None, sg)
                    return cache[key]
                cache[key] = (None, sg)
                return cache[key]

            cache[key] = (sg, None) if member_count != 2 else (sg, None, None)
            return cache[key]

        # count >= 2: pick based on successful bans
        selected = next((sg for sg in annotated if not sg.has_successful_ban_by_others), None)

        # If everything is successfully banned-by-others, selected_game must be None.
        if selected is None:
            banned_any = next((sg for sg in annotated if sg.has_successful_ban_by_others), None)
            if member_count == 2:
                cache[key] = (None, None, banned_any)
                return cache[key]
            cache[key] = (None, banned_any)
            return cache[key]

        banned = next(
            (sg for sg in annotated
             if sg.pk != selected.pk and getattr(sg, 'has_successful_ban_by_others', False)),
            None
        )

        if member_count == 2:
            selected_two = next((sg for sg in annotated if sg.pk != selected.pk), None)
            if selected_two and getattr(selected_two, "has_successful_ban_by_others", False):
                selected_two = None
            cache[key] = (selected, selected_two, banned)
            return cache[key]

        cache[key] = (selected, banned)
        return cache[key]

    def _unpack_resolved(self, obj):
        """
        Normalizes _resolve_games_for_participant output to:
            (selected, selected_two, banned)
        where selected_two is None for 3+ leagues.
        """
        resolved = self._resolve_games_for_participant(obj)
        if len(resolved) == 2:
            selected, banned = resolved
            return selected, None, banned
        selected, selected_two, banned = resolved
        return selected, selected_two, banned

    # ---- public getters -----------------------------------------------------
    def get_selected_games(self, obj):
        league = self.context.get('league')
        if not league:
            return []

        member_count = self._league_member_count()
        successful_ban_threshold = 1 if member_count == 2 else 2

        from django.db.models import Count, Q  # local import to keep file-level imports minimal
        qs = (
            SelectedGame.objects
            .filter(profile=obj.profile, league=league)
            .annotate(
                bans_by_others_count=Count(
                    "bandecision",
                    filter=Q(
                        bandecision__league=league,
                        bandecision__player_banning__isnull=False,
                    ) & ~Q(bandecision__player_banning=obj.profile),
                    distinct=True,
                )
            )
            .filter(bans_by_others_count__lt=successful_ban_threshold)
            .select_related('game')
            .order_by('id')
        )

        return SelectedGameSerializer(qs, many=True, context=self.context).data

    def get_first_game_selection_banned_by_others(self, obj):
        _, _, banned = self._unpack_resolved(obj)
        return SelectedGameSerializer(banned, context=self.context).data if banned else None

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return bool(league and obj == league.active_player)

