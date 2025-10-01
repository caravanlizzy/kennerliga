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
    banned_selected_game = serializers.SerializerMethodField()
    has_banned = serializers.BooleanField(read_only=True)
    is_active_player = serializers.SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = [
            'id',
            'username',
            'profile_name',
            'selected_game',
            'banned_selected_game',   # NEW
            'has_banned',
            'is_active_player',
            'rank',
        ]

    # ---- internal helper & cache -------------------------------------------
    def _resolve_games_for_participant(self, obj):
        """
        Returns a tuple: (selected_sg, banned_sg)
        - selected_sg: preferred unbanned-by-others pick; fallback deterministic.
        - banned_sg: the "other" pick if present; otherwise None.
        """
        # Per-serializer cache so both getters don't redo work
        cache = getattr(self, '_sg_cache', None)
        if cache is None:
            cache = self._sg_cache = {}

        key = obj.pk
        if key in cache:
            return cache[key]

        league = self.context.get('league')
        if not league:
            cache[key] = (None, None)
            return cache[key]

        qs = SelectedGame.objects.filter(player=obj.profile, league=league)

        count = qs.count()
        if count == 0:
            cache[key] = (None, None)
            return cache[key]

        if count == 1:
            sg = qs.select_related('game').first()
            cache[key] = (sg, None)
            return cache[key]

        # count >= 2: annotate bans by others and pick
        bans_by_others = BanDecision.objects.filter(
            league=league,
            selected_game=OuterRef('pk')
        ).exclude(player_banning=obj.profile)

        annotated = (qs
                     .annotate(has_ban_by_others=Exists(bans_by_others))
                     .select_related('game')
                     .order_by('id'))

        # Preferred selected: first unbanned-by-others
        selected = next((sg for sg in annotated if not sg.has_ban_by_others), None)

        if selected is None:
            # All banned (or no unbanned found): deterministic fallback is smallest id
            selected = annotated.first()

        # banned candidate: the "other" one, prefer one that IS banned-by-others
        banned = next((sg for sg in annotated if sg.pk != selected.pk and getattr(sg, 'has_ban_by_others', False)), None)
        if banned is None:
            # If none explicitly banned (e.g., >2 picks all unbanned), pick a different one deterministically
            banned = next((sg for sg in annotated if sg.pk != selected.pk), None)

        cache[key] = (selected, banned)
        return cache[key]

    # ---- public getters -----------------------------------------------------
    def get_selected_game(self, obj):
        selected, _ = self._resolve_games_for_participant(obj)
        return SelectedGameSerializer(selected, context=self.context).data if selected else None

    def get_banned_selected_game(self, obj):
        _, banned = self._resolve_games_for_participant(obj)
        return SelectedGameSerializer(banned, context=self.context).data if banned else None

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return bool(league and obj == league.active_player)

