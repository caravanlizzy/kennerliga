from collections import defaultdict

from django.db.models import Count, Exists, OuterRef
from rest_framework import serializers

from game.models import BanDecision
from league.models import League
from season.serializer import SeasonParticipantSerializer


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class LeagueDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ['id', 'status', 'season', 'level', 'active_player', 'members']

    def get_members(self, league):
        # Render members with your existing participant serializer
        members_qs = (
            league.members
            .select_related('profile__user')
            .annotate(
                has_banned=Exists(
                    BanDecision.objects.filter(
                        league=league,
                        player_banning_id=OuterRef('profile_id'),
                    )
                )
            )
            .order_by('rank')
        )
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
