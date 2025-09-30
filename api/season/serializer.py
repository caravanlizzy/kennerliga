from django.db.models import OuterRef, Exists
from rest_framework import serializers

from game.models import SelectedGame, BanDecision
from game.serializers import SelectedGameSerializer
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
    username = serializers.CharField(source='profile.user.username', read_only=True)
    profile_name = serializers.CharField(source='profile.profile_name', read_only=True)
    selected_game = serializers.SerializerMethodField()
    has_banned = serializers.BooleanField(read_only=True)
    is_active_player = serializers.SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            'id',
            'username',
            'profile_name',
            'selected_game',
            'has_banned',
            'is_active_player',
            'rank',
        ]

    def get_selected_game(self, obj):
        """
        Pick this participant's selected game for the given league:
        - If there are two, prefer the one NOT banned by others; tie-breaker: smallest id.
        - If there is one, return it (keeps your original behavior).
        - If none, return None.
        """
        league = self.context.get('league')
        if not league:
            return None

        qs = SelectedGame.objects.filter(player=obj.profile, league=league)

        # Fast path: 0 or 1
        count = qs.count()
        if count == 0:
            return None
        if count == 1:
            sg = qs.select_related('game').first()
            return SelectedGameSerializer(sg, context=self.context).data

        # Exactly 2 (or more: guard) → prefer unbanned-by-others
        bans_by_others = BanDecision.objects.filter(
            league=league,
            selected_game=OuterRef('pk')
        ).exclude(player_banning=obj.profile)

        sg = (qs.annotate(has_ban_by_others=Exists(bans_by_others))
                .filter(has_ban_by_others=False) # the selected game after banning (must have 0 bans)
                .select_related('game')
                .first())

        if not sg:
            # both banned (or unexpected >2) → fall back deterministically
            sg = qs.order_by('id').select_related('game').first()

        return SelectedGameSerializer(sg, context=self.context).data if sg else None

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return bool(league and obj == league.active_player)
