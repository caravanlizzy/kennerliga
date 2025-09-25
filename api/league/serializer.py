from collections import defaultdict

from django.db.models import Count
from rest_framework import serializers

from game.models import BanDecision
from league.models import League
from season.serializer import SeasonParticipantSerializer


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


# class LeagueMemberSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='profile.user.username', read_only=True)
#     profile_name = serializers.CharField(source='profile.profile_name', read_only=True)
#     selected_game = serializers.SerializerMethodField()
#     game = serializers.SerializerMethodField()
#     is_active_player = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SeasonParticipant
#         fields = ['id', 'username', 'profile_name', 'selected_game', 'game', 'is_active_player']
#
#     def get_selected_game(self, participant):
#         selected_game = SelectedGame.objects.filter(
#             player=participant.profile,
#             league=self.context['league']
#         ).first()
#         return str(selected_game.game) if selected_game else None
#
#     def get_banned_game(self, participant):
#         ban = BanDecision.objects.filter(
#             player=participant.profile,
#             league=self.context['league']
#         ).first()
#         return str(ban.banned_game.game) if ban and ban.banned_game else None
#
#     def get_is_active_player(self, participant):
#         league = self.context.get('league')
#         return league.active_player_id == participant.id if league else False


class LeagueDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ['id', 'status', 'season', 'level', 'active_player', 'members']

    def get_members(self, league):
        # Render members with your existing participant serializer
        members_qs = league.members.all().order_by('rank')
        serializer = SeasonParticipantSerializer(
            members_qs,
            many=True,
            context={'league': league}
        )
        data = serializer.data

        # Collect selected_game IDs that appear in the payload
        sg_ids = []
        for m in data:
            sg = m.get('selected_game') or {}
            sg_id = sg.get('id')
            if sg_id:
                sg_ids.append(sg_id)

        # Build: selected_game_id -> [banning_profile_name, ...]
        bans_map = defaultdict(list)
        if sg_ids:
            for sg_id, name in (
                BanDecision.objects
                .filter(league=league, selected_game_id__in=sg_ids)
                .select_related('player_banning')
                .values_list('selected_game_id', 'player_banning__user__username')
            ):
                bans_map[sg_id].append(name)

        # Enrich each member with banned_by (and position + selected_game_id)
        for i, member in enumerate(data, 1):
            member['position'] = i
            sg = member.get('selected_game') or {}
            sg_id = sg.get('id')
            member['selected_game_id'] = sg_id  # optional, handy for FE actions
            member['banned_by'] = bans_map.get(sg_id, [])

            # If you don't want to send heavy banned_game details anymore:
            if 'banned_game' in member:
                member.pop('banned_game', None)  # or keep only an id if you prefer

        return data



