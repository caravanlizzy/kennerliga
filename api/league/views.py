from django.db.models import Prefetch, Count
from django.db.models import prefetch_related_objects
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.constants import get_ban_amount_for_success
from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding, GameStanding, LeagueTieResolution, LeagueTieResolutionEntry, TieResolutionReason
from league.serializer import LeagueDetailSerializer, LeagueStandingSerializer, GameStandingSerializer, LeagueSerializer, LeagueListSerializer
from services.standings_snapshot import rebuild_league_snapshot, rebuild_game_snapshot
from league.services import advance_turn, get_full_standings_data


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all().prefetch_related(
        "members__profile", "members__profile__user"
    ).order_by("season__year", "season__month", "level")
    serializer_class = LeagueSerializer
    filterset_fields = ['season', 'members__profile']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return LeagueListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['rebuild_standings', 'resolve_tie']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], url_path='standings')
    def standings(self, request, pk=None):
        qs = (
            LeagueStanding.objects
            .filter(league=pk)
            .select_related("player_profile")
            .order_by("-league_points", "-wins", "-tie_break_priority", "player_profile__profile_name")
        )
        return Response(LeagueStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='game-standings')
    def game_standings(self, request, pk=None):
        sg_id = request.query_params.get("selected_game")
        if not sg_id:
            return Response({"detail": "selected_game is required."}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            GameStanding.objects
            .filter(league=pk, selected_game_id=sg_id)
            .select_related("player_profile__user")
            .order_by("rank", "player_profile__profile_name")
        )
        return Response(GameStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='full-standings')
    def full_standings(self, request, pk=None):
        league = self.get_object()
        data = get_full_standings_data(league)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rebuild-standings')
    def rebuild_standings(self, request, pk=None):
        """
        Rebuilds ALL per-game standings (GameStanding) for this league,
        then rebuilds the overall league standings (LeagueStanding),
        and returns the fresh LeagueStanding list.
        """
        league = self.get_object()



        # Optional: allow client to specify win_mode, defaulting to "fractional"
        win_mode = request.data.get("win_mode", "fractional")

        # 1) Rebuild per-game snapshots for all SelectedGames in this league
        selected_games = SelectedGame.objects.filter(league=league).select_related("game")
        for sg in selected_games:
            rebuild_game_snapshot(sg, win_mode=win_mode)

        # 2) Rebuild league snapshot (LeagueStanding) based on all results
        rebuild_league_snapshot(league, win_mode=win_mode)

        # 3) Return refreshed league standings
        qs = (
            LeagueStanding.objects
            .filter(league=league)
            .select_related("player_profile__user")
            .order_by("-league_points", "-wins", "-tie_break_priority", "player_profile__profile_name")
        )
        return Response(LeagueStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='resolve-tie')
    def resolve_tie(self, request, pk=None):
        """
        Admin-only endpoint to resolve a general tie group by providing a
        group_key, a reason, and the exact player order within the tied group.

        Expected payload example:
        {
          "group_key": "lp:12.00|w:5.00",
          "reason": "WINNER_PERCENTAGE"|"CANT_STOP",
          "player_order": [player_profile_id_1, player_profile_id_2, ...],
          "note": "optional"
        }
        """
        league = self.get_object()

        group_key = request.data.get("group_key")
        reason_raw = request.data.get("reason")
        player_order = request.data.get("player_order", [])
        note = request.data.get("note")

        if group_key is None or reason_raw is None or not isinstance(player_order, list) or len(player_order) == 0:
            return Response({
                "detail": "group_key, reason and non-empty player_order are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate reason against enum
        if reason_raw not in dict(TieResolutionReason.choices):
            return Response({
                "detail": f"Invalid reason. Allowed: {list(dict(TieResolutionReason.choices).keys())}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ensure all players belong to this league
        valid_ids = set(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
            .values_list('player_profile_id', flat=True)
        )
        if set(player_order) != valid_ids:
            return Response({
                "detail": "player_order must contain only player_profile ids present in this league standings."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Optional: verify that listed players currently match the provided group_key
        current_groups = set(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
            .values_list('unresolved_tie_group', flat=True)
        )
        # If players are already resolved, their group will be None; allow that (admin may re-order).
        # But if any non-None groups exist and they differ from group_key, warn.
        mismatched = [g for g in current_groups if g not in (None, group_key)]
        if mismatched:
            return Response({
                "detail": f"Provided group_key does not match current standings groups: {sorted(set(mismatched))}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Upsert resolution by (league, group_key)
        resolution, _created = LeagueTieResolution.objects.update_or_create(
            league=league,
            group_key=group_key,
            defaults={
                'reason': reason_raw,
                'note': note,
                'is_resolved': True,
            }
        )

        # Replace entries
        resolution.entries.all().delete()
        LeagueTieResolutionEntry.objects.bulk_create([
            LeagueTieResolutionEntry(
                resolution=resolution,
                player_profile_id=pp_id,
                order_index=index + 1,
            ) for index, pp_id in enumerate(player_order)
        ])

        # Update LeagueStanding: clear tie group and set tie priorities for these players
        standings = list(
            LeagueStanding.objects.filter(league=league, player_profile_id__in=player_order)
        )
        # Highest priority for first in order
        max_priority = len(player_order)
        id_to_priority = {pp_id: (max_priority - idx) for idx, pp_id in enumerate(player_order)}

        for ls in standings:
            ls.unresolved_tie_group = None
            ls.tie_break_priority = id_to_priority.get(ls.player_profile_id, 0)

        LeagueStanding.objects.bulk_update(standings, [
            'unresolved_tie_group', 'tie_break_priority'
        ])

        # Return refreshed standings
        qs = (
            LeagueStanding.objects
            .filter(league=league)
            .select_related("player_profile__user")
            .order_by("-league_points", "-wins", "-tie_break_priority", "player_profile__profile_name")
        )
        return Response(LeagueStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='set-active-player')
    def set_active_player(self, request, pk=None):
        """
        Set the active player for the league using a profile_id.
        Expects profile_id in the request data.
        """
        league = self.get_object()
        profile_id = request.data.get('profile_id')

        if not profile_id:
            return Response(
                {"detail": "profile_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the SeasonParticipant with the given profile_id in this league
        try:
            season_participant = league.members.get(profile_id=profile_id)
        except league.members.model.DoesNotExist:
            return Response(
                {"detail": "Profile is not a member of this league."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the active player
        league.active_player = season_participant
        league.save(update_fields=['active_player'])

        return Response({"participant_id": season_participant.id}, status=status.HTTP_200_OK)


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
                    .select_related('game')
                    .prefetch_related('result_set'),  # Added prefetch for results
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

