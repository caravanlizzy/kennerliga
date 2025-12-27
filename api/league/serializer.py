from collections import defaultdict

from django.db.models import Count, Exists, OuterRef
from rest_framework import serializers

from game.models import BanDecision
from league.models import League, GameStanding, LeagueStanding
from season.models import SeasonParticipant
from season.serializer import SeasonParticipantSerializer, SeasonParticipantMiniSerializer


class LeagueSerializer(serializers.ModelSerializer):
    # write: accept SP ids
    member_ids = serializers.PrimaryKeyRelatedField(
        source="members",
        queryset=SeasonParticipant.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    # read: return mini objects
    members = SeasonParticipantMiniSerializer(many=True, read_only=True)

    class Meta:
        model = League
        fields = ["id", "season", "level", "status", "active_player", "members", "member_ids"]

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
    profile_name = serializers.CharField(source="player_profile.profile_name", read_only=True)
    user_id = serializers.IntegerField(source="player_profile.user.id", read_only=True)
    username = serializers.CharField(source="player_profile.user.username", read_only=True)

    class Meta:
        model = LeagueStanding
        fields = ("player_profile", "profile_name", "user_id", "username", "wins", "league_points")


class GameStandingSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(source="player_profile.profile_name", read_only=True)
    user_id = serializers.IntegerField(source="player_profile.user.id", read_only=True)
    username = serializers.CharField(source="player_profile.user.username", read_only=True)

    class Meta:
        model = GameStanding
        fields = ("player_profile", "profile_name", "user_id", "username", "selected_game", "points", "rank", "league_points", "win_share")


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

        # Enrich each member with position only
        for i, member in enumerate(data, 1):
            member['position'] = i

            # If you don't want to send heavy banned_game details anymore:
            if 'banned_game' in member:
                member.pop('banned_game', None)

            # Ensure we don't expose these fields if they were previously added
            member.pop('selected_game_id', None)
            member.pop('banned_by', None)

            # In case you previously injected banned_by into nested objects
            for sg in (member.get("selected_games") or []):
                if isinstance(sg, dict):
                    sg.pop("banned_by", None)

            banned_sg = member.get("first_game_selection_banned_by_others")
            if isinstance(banned_sg, dict):
                banned_sg.pop("banned_by", None)

        return data
