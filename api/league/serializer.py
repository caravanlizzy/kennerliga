from collections import defaultdict

from django.db.models import Count, Exists, OuterRef
from rest_framework import serializers

from game.models import BanDecision
from league.models import League, GameStanding, LeagueStanding
from season.models import SeasonParticipant
from season.serializer import SeasonParticipantSerializer


class LeagueSerializer(serializers.ModelSerializer):
    # Accept a list of SeasonParticipant IDs
    members = serializers.PrimaryKeyRelatedField(
        queryset=SeasonParticipant.objects.all(), many=True
    )

    class Meta:
        model = League
        fields = ["id", "season", "level", "status", "active_player", "members"]

    def validate(self, attrs):
        season = attrs.get("season") or getattr(self.instance, "season", None)
        members = attrs.get("members", [])
        # Ensure all members are from the same season
        invalid = [sp.id for sp in members if sp.season_id != season.id]
        if invalid:
            raise serializers.ValidationError(
                {"members": f"All members must belong to season {season.id}. Offenders: {invalid}"}
            )
        return attrs

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        league = League.objects.create(**validated_data)
        league.members.set(members)
        return league

class LeagueStandingSerializer(serializers.ModelSerializer):
    player = serializers.CharField(source="player_profile.profile_name", read_only=True)

    class Meta:
        model = LeagueStanding
        fields = ("player_profile", "player", "wins", "league_points")


class GameStandingSerializer(serializers.ModelSerializer):
    player = serializers.CharField(source="player_profile.profile_name", read_only=True)

    class Meta:
        model = GameStanding
        fields = ("player_profile", "player", "selected_game", "points", "rank", "league_points", "win_share")


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
