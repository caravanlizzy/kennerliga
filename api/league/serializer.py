from collections import defaultdict

from django.db.models import Count, Exists, OuterRef
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers

from game.models import BanDecision
from league.models import League, GameStanding, LeagueStanding
from season.models import SeasonParticipant


class LeagueSerializer(serializers.ModelSerializer):
    # write: accept SP ids
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=SeasonParticipant.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    # read: return mini objects
    members = SerializerMethodField()
    is_completed = SerializerMethodField()

    class Meta:
        model = League
        fields = ["id", "season", "level", "status", "active_player", "members", "member_ids", "is_completed"]

    def get_is_completed(self, obj):
        from league.queries import is_league_finished
        return is_league_finished(obj)

    def get_members(self, obj):
        # We want to include selected_games for the season list page's icons
        # Use SeasonParticipantSerializer and pass the league in context
        from season.serializer import SeasonParticipantSerializer
        return SeasonParticipantSerializer(obj.members.all(), many=True, context={'league': obj}).data

    def validate(self, attrs):
        season = attrs.get("season") or getattr(self.instance, "season", None)
        members = attrs.get("member_ids", [])
        if season and members:
            # Ensure all members are from the same season
            invalid = [sp.id for sp in members if sp.season_id != season.id]
            if invalid:
                raise serializers.ValidationError(
                    {"member_ids": f"All members must belong to season {season.id}. Offenders: {invalid}"}
                )
        return attrs

    def create(self, validated_data):
        members = validated_data.pop("member_ids", [])
        league = League.objects.create(**validated_data)
        league.members.set(members)
        return league

    def update(self, instance, validated_data):
        members = validated_data.pop("member_ids", None)
        league = super().update(instance, validated_data)
        if members is not None:
            league.members.set(members)
        return league

class LeagueListSerializer(serializers.ModelSerializer):
    is_completed = SerializerMethodField()

    class Meta:
        model = League
        fields = ["id", "season", "level", "status", "active_player", "is_completed"]

    def get_is_completed(self, obj):
        from league.queries import is_league_finished
        return is_league_finished(obj)

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
        from season.serializer import SeasonParticipantSerializer
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

        return data
