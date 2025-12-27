from django.db.models import Prefetch
from django.db.models import prefetch_related_objects
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding, GameStanding
from league.serializer import LeagueDetailSerializer, LeagueStandingSerializer, GameStandingSerializer, LeagueSerializer
from services.standings_snapshot import rebuild_league_snapshot, rebuild_game_snapshot


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all().prefetch_related(
        "members__profile", "members__profile__user"
    ).order_by("season__year", "season__month", "level")
    serializer_class = LeagueSerializer
    filterset_fields = ['season', 'members__profile']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'rebuild_standings':
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], url_path='standings')
    def standings(self, request, pk=None):
        qs = (
            LeagueStanding.objects
            .filter(league=pk)
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
            .filter(league=pk, selected_game_id=sg_id)
            .select_related("player_profile")
            .order_by("rank", "player_profile__profile_name")
        )
        return Response(GameStandingSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='full-standings')
    def full_standings(self, request, pk=None):
        """
        Returns a matrix suitable for a standings table:
        - Rows: players ordered by total league_points (desc)
        - Columns: per-game data (points & league_points for each selected_game)

        Response shape:
        {
          "selected_games": [
            {"id": 1, "game_name": "Catan"},
            {"id": 2, "game_name": "Azul"},
            ...
          ],
          "standings": [
            {
              "player_profile_id": 5,
              "profile_name": "Alice",
              "total_league_points": "18.00",
              "total_wins": "3.00",
              "games": {
                "1": {"points": "120.00", "league_points": "6.00", "rank": 1},
                "2": {"points": "85.50", "league_points": "3.00", "rank": 2},
                ...
              }
            },
            ...
          ]
        }
        """
        league = self.get_object()

        # 1. Get all selected games for this league (column headers)
        selected_games = (
            SelectedGame.objects
            .filter(league=league)
            .select_related('game')
            .order_by('id')
        )
        selected_game_list = [
            {"id": sg.id, "game_name": sg.game.name, "game_short_name": sg.game.short_name}
            for sg in selected_games
        ]
        selected_game_ids = [sg.id for sg in selected_games]

        # 2. Get league standings (for row ordering & totals)
        league_standings = (
            LeagueStanding.objects
            .filter(league=league)
            .select_related('player_profile')
            .order_by('-league_points', '-wins', 'player_profile__profile_name')
        )

        # 3. Get all game standings for this league
        game_standings = (
            GameStanding.objects
            .filter(league=league)
            .select_related('player_profile')
        )

        # Build a lookup: {player_profile_id: {selected_game_id: {...}}}
        game_data_by_player = {}
        for gs in game_standings:
            pid = gs.player_profile_id
            if pid not in game_data_by_player:
                game_data_by_player[pid] = {}
            game_data_by_player[pid][gs.selected_game_id] = {
                "points": str(gs.points),
                "league_points": str(gs.league_points),
                "rank": gs.rank,
            }

        # 4. Build the response rows
        standings_list = []
        for ls in league_standings:
            pid = ls.player_profile_id
            player_games = game_data_by_player.get(pid, {})

            # Build games dict keyed by selected_game_id (as string for JSON)
            games_dict = {}
            for sg_id in selected_game_ids:
                if sg_id in player_games:
                    games_dict[str(sg_id)] = player_games[sg_id]
                else:
                    games_dict[str(sg_id)] = {"points": None, "league_points": None, "rank": None}

            standings_list.append({
                "player_profile_id": pid,
                "profile_name": ls.player_profile.profile_name,
                "total_league_points": str(ls.league_points),
                "total_wins": str(ls.wins),
                "games": games_dict,
            })

        return Response({
            "selected_games": selected_game_list,
            "standings": standings_list,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rebuild-standings')
    def rebuild_standings(self, request, pk=None):
        """
        Rebuilds ALL per-game standings (GameStanding) for this league,
        then rebuilds the overall league standings (LeagueStanding),
        and returns the fresh LeagueStanding list.
        """
        league = self.get_object()



        # Optional: allow client to specify win_mode, defaulting to "count_top_block"
        win_mode = request.data.get("win_mode", "count_top_block")

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
            .select_related("player_profile")
            .order_by("-league_points", "-wins", "player_profile__profile_name")
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

