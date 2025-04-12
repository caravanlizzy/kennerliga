from rest_framework import serializers

from game.models import BanDecision, SelectedGame
from league.models import League
from season.models import SeasonParticipant


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class LeagueMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.user.username', read_only=True)
    profile_name = serializers.CharField(source='profile.profile_name', read_only=True)
    selected_game = serializers.SerializerMethodField()
    banned_game = serializers.SerializerMethodField()
    is_active_player = serializers.SerializerMethodField()

    class Meta:
        model = SeasonParticipant
        fields = ['id', 'username', 'profile_name', 'selected_game', 'banned_game', 'is_active_player']

    def get_selected_game(self, participant):
        selected_game = SelectedGame.objects.filter(
            player=participant.profile,
            league=self.context['league']
        ).first()
        return str(selected_game.game) if selected_game else None

    def get_banned_game(self, participant):
        ban = BanDecision.objects.filter(
            player=participant.profile,
            league=self.context['league']
        ).first()
        return str(ban.banned_game.game) if ban and ban.banned_game else None

    def get_is_active_player(self, participant):
        league = self.context.get('league')
        return league.active_player_id == participant.id if league else False

class LeagueDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ['id', 'status', 'season', 'level', 'active_player', 'members']

    def get_members(self, league):
        members = league.members.all()
        return LeagueMemberSerializer(
            members,
            many=True,
            context={'league': league}
        ).data



