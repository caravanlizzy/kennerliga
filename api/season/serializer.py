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

    def get_selected_game(self, obj):
        league = self.context.get('league')
        if not league:
            return None

        qs = SelectedGame.objects.filter(player=obj.profile, league=league)

        selected_games_count = qs.count()

        if selected_games_count == 0:
            selected_game = None

        elif selected_games_count == 1:
            selected_game = qs.first()

        elif selected_games_count == 2:
            # Any ban by someone else against THIS selected game
            bans_by_others = BanDecision.objects.filter(
                league=league,
                selected_game=OuterRef('pk'),
            ).exclude(player_banning=obj.profile)

            selected_game = (
                qs.annotate(has_ban_by_others=Exists(bans_by_others))
                .filter(has_ban_by_others=False)
                .order_by('id')  # tie-breaker if both unbanned
                .first()
            )

        else:
            raise Exception("More than 2 selected games for a player in a league.")

        return SelectedGameSerializer(selected_game).data if selected_game else None

    def get_banned_game(self, obj):
        league = self.context.get('league')
        if not league:
            return None

        ban = (BanDecision.objects
               .filter(league=league, selected_game__player=obj.profile)
               .select_related('selected_game__game')
               .first())
        return SelectedGameSerializer(ban.selected_game).data if ban else None

    def get_is_active_player(self, obj):
        league = self.context.get('league')
        return obj == league.active_player if league else False
