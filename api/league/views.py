from django.db.models import Prefetch
from django.db.models import prefetch_related_objects
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding, GameStanding
from league.serializer import LeagueDetailSerializer, LeagueStandingSerializer, GameStandingSerializer, LeagueSerializer
from services.standings_snapshot import rebuild_league_snapshot


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]  # adjust to your needs
    filterset_fields = ['season', '']

    @action(detail=True, methods=['get'], url_path='standings')
    def standings(self, request, pk=None):
        qs = (
            LeagueStanding.objects
            .filter(league_id=pk)
            .select_related("player_profile")
            .order_by("-league_points", "-wins", "player_profile__profile_name")
        )
        return Response(LeagueStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='game-standings')
    def game_standings(self, request, pk=None):
        sg_id = request.query_params.get("selected_game")
        if not sg_id:
            return Response({"detail": "selected_game is required."}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            GameStanding.objects
            .filter(league_id=pk, selected_game_id=sg_id)
            .select_related("player_profile")
            .order_by("rank", "player_profile__profile_name")
        )
        return Response(GameStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rebuild-standings')
    def rebuild_standings(self, request, pk=None):
        league = self.get_object()
        rebuild_league_snapshot(league)
        qs = (
            LeagueStanding.objects
            .filter(league=league)
            .select_related("player_profile")
            .order_by("-league_points", "-wins", "player_profile__profile_name")
        )
        return Response(LeagueStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class LeagueDetailViewSet(ReadOnlyModelViewSet):
    serializer_class = LeagueDetailSerializer
    queryset = League.objects.select_related('season', 'active_player__profile__user')

    def retrieve(self, request, *args, **kwargs):
        league = self.get_object()

        members_qs = (
            league.members
            .select_related('profile__user')
            .order_by('rank', 'id')
            .prefetch_related(
                # Prefetch all selected games of this player in this league
                Prefetch(
                    'profile__selected_games',
                    queryset=SelectedGame.objects
                    .filter(league=league)
                    .select_related('game'),
                    to_attr='selected_in_this_league',
                ),
                # Prefetch bans made BY this player (via player_banning)
                Prefetch(
                    'profile__ban_decisions',
                    queryset=BanDecision.objects
                    .filter(league=league)
                    .select_related('selected_game__game'),
                    to_attr='bans_made_in_this_league',
                ),
                # Prefetch bans AGAINST this player’s selected games
                Prefetch(
                    'profile__selected_games__bandecision_set',
                    queryset=BanDecision.objects
                    .filter(league=league)
                    .select_related('player_banning', 'selected_game__game'),
                    to_attr='bans_against_in_this_league',
                ),
            )
        )

        # Attach prefetch to this instance
        prefetch_related_objects([league], Prefetch('members', queryset=members_qs))

        serializer = LeagueDetailSerializer(
            league,
            context={'league': league}
        )
        return Response(serializer.data)

