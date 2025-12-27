from collections import defaultdict

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction

from game.models import SelectedGame, ResultConfig, TieBreaker
from league.models import GameStanding
from league.serializer import GameStandingSerializer
from season.models import Season
from season.serializer import SeasonSerializer
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot
from .models import Result
from .serializers import ResultSerializer


class IsAdminOrMemberInCurrentLeague(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # For 'create' action, we need to check the SelectedGame in the payload
        if view.action == 'create':
            selected_game_id = request.data.get('selected_game')
            if not selected_game_id:
                return False

            try:
                selected_game = SelectedGame.objects.select_related('league__season').get(id=selected_game_id)
                season = selected_game.league.season

                # Check if season is current  or RUNNING)
                if season.status != Season.SeasonStatus.RUNNING:
                    return False

                # Check if user is a member of the league
                # League.members is M2M to SeasonParticipant. SeasonParticipant.profile.user = user
                return selected_game.league.members.filter(profile__user=request.user).exists()
            except SelectedGame.DoesNotExist:
                return False

        return True


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ['selected_game', 'player_profile']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminOrMemberInCurrentLeague]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class MatchResultViewSet(ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminOrMemberInCurrentLeague]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def _fnum(self, x, default=None):
        try:
            return float(x)
        except (TypeError, ValueError):
            return default

    def _get_tie_groups(self, rows, base_field, use_points, tbs, level):
        def key_up_to(row, lvl):
            base_val = self._fnum(row.get(base_field), 0)
            key = [-base_val] if use_points else [base_val]
            for i in range(lvl + 1):
                if i < 0: continue
                tb = tbs[i]
                val = self._fnum(row.get("tie_breaker_value"))
                if val is None:
                    key.append(float("inf"))
                else:
                    key.append(-val if tb.higher_wins else val)
            return tuple(key)

        groups = defaultdict(list)
        for r in rows:
            groups[key_up_to(r, level)].append(r)
        return [g for g in groups.values() if len(g) > 1]

    def _finalize_results(self, serializers, rows, base_field, use_points, tbs, selected_game, league, decisive_tb=None,
                          needing_pids=None):
        if needing_pids is None:
            needing_pids = set()

        def get_full_sort_key(row):
            base_val = self._fnum(row.get(base_field), 0)
            key = [-base_val] if use_points else [base_val]
            for tb in tbs:
                val = self._fnum(row.get("tie_breaker_value"))
                key.append(float("inf") if val is None else (-val if tb.higher_wins else val))
            return tuple(key)

        sorted_rows = sorted(rows, key=get_full_sort_key)
        pid_to_rank = {}
        current_rank = 1
        for i, row in enumerate(sorted_rows):
            if i > 0 and get_full_sort_key(row) != get_full_sort_key(sorted_rows[i - 1]):
                current_rank = i + 1
            pid_to_rank[row["player_profile"].id] = current_rank

        with transaction.atomic():
            saved = []
            for s in serializers:
                row_data = s.validated_data
                pid = row_data["player_profile"].id
                row_data["position"] = pid_to_rank[pid]
                row_data["tie_breaker_resolved"] = True
                if decisive_tb and pid in needing_pids:
                    row_data["decisive_tie_breaker"] = decisive_tb
                saved.append(s.save())

            rebuild_game_snapshot(selected_game, win_mode="count_top_block")
            rebuild_league_snapshot(league, win_mode="count_top_block")

        standings = GameStanding.objects.filter(league=league, selected_game=selected_game.id).select_related(
            "player_profile").order_by("rank", "player_profile__profile_name")
        return Response({
            "results": ResultSerializer(saved, many=True).data,
            "game_standings": GameStandingSerializer(standings, many=True).data,
        }, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        selected_game_id = request.data.get("selected_game")
        data = request.data.get("results", [])
        requested_tb_id = (request.data.get("tiebreaker") or {}).get("id")

        if not selected_game_id or not isinstance(data, list) or len(data) < 2:
            return Response({"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_game = SelectedGame.objects.select_related("game", "league__season").get(pk=selected_game_id)
            result_config = ResultConfig.objects.get(game=selected_game.game)
        except (SelectedGame.DoesNotExist, ResultConfig.DoesNotExist):
            return Response({"detail": "Game or Config not found."}, status=status.HTTP_404_NOT_FOUND)

        league, season, tbs = selected_game.league, selected_game.league.season, list(
            TieBreaker.objects.filter(result_config=result_config).order_by("-order"))
        use_points, base_field = result_config.has_points, ("points" if result_config.has_points else "position")

        if len(data) != league.members.count():
            return Response({"detail": "Incorrect result count."}, status=status.HTTP_400_BAD_REQUEST)

        serializers, seen = [], set()
        for entry in data:
            entry.update({"selected_game": selected_game.id, "league": league.id, "season": season.id})
            if entry.get("player_profile") in seen:
                return Response({"detail": "Duplicate player."}, status=status.HTTP_400_BAD_REQUEST)
            seen.add(entry.get("player_profile"))
            s = ResultSerializer(data=entry, context={"request": request})
            if not s.is_valid(): return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializers.append(s)

        rows = [s.validated_data for s in serializers]

        # Initial tie check
        if requested_tb_id is None:
            groups = self._get_tie_groups(rows, base_field, use_points, tbs, -1)
            if not groups or not tbs:
                return self._finalize_results(serializers, rows, base_field, use_points, tbs, selected_game, league)

            next_tb = tbs[0]
            return Response({
                "detail": "Tie detected.", "unresolved_tie": True,
                "required_tie_breaker": {"id": next_tb.id, "name": next_tb.name, "order": next_tb.order,
                                         "higher_wins": next_tb.higher_wins},
                "tie_groups": [{"points": g[0].get("points"), "position": g[0].get("position"),
                                "players": [r["player_profile"].id for r in g]} for g in groups]
            }, status=status.HTTP_202_ACCEPTED)

        # TB Resolution
        tb_map = {tb.id: idx for idx, tb in enumerate(tbs)}
        if requested_tb_id not in tb_map:
            return Response({"detail": "Invalid TB."}, status=status.HTTP_400_BAD_REQUEST)

        level = tb_map[requested_tb_id]
        prev_groups = self._get_tie_groups(rows, base_field, use_points, tbs, level - 1)
        needing_pids = {r["player_profile"].id for g in prev_groups for r in g}

        if any(self._fnum(r.get("tie_breaker_value")) is None for r in rows if r["player_profile"].id in needing_pids):
            return Response({"detail": "Missing TB values.", "required_tie_breaker": {"id": requested_tb_id}},
                            status=status.HTTP_400_BAD_REQUEST)

        remaining = self._get_tie_groups(rows, base_field, use_points, tbs, level)
        if remaining and level + 1 < len(tbs):
            next_tb = tbs[level + 1]
            return Response({
                "detail": "Still tied.", "unresolved_tie": True,
                "required_tie_breaker": {"id": next_tb.id, "name": next_tb.name, "order": next_tb.order,
                                         "higher_wins": next_tb.higher_wins},
                "tie_groups": [{"points": g[0].get("points"), "position": g[0].get("position"),
                                "players": [r["player_profile"].id for r in g]} for g in remaining]
            }, status=status.HTTP_202_ACCEPTED)

        return self._finalize_results(serializers, rows, base_field, use_points, tbs, selected_game, league,
                                      decisive_tb=tbs[level], needing_pids=needing_pids)

    def list(self, request):
        season_id = request.query_params.get("season")
        league = request.query_params.get("league")
        selected_game_id = request.query_params.get("selected_game")
        if not all([season_id, league, selected_game_id]):
            return Response({"detail": "Parameters required."}, status=status.HTTP_400_BAD_REQUEST)
        qs = Result.objects.filter(season_id=season_id, league=league, selected_game_id=selected_game_id)
        return Response(ResultSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            obj = Result.objects.get(pk=pk)
            return Response(ResultSerializer(obj).data)
        except Result.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="seasons-with-results")
    def seasons_with_results(self, request):
        seasons = Season.objects.filter(results__isnull=False).distinct()
        return Response(SeasonSerializer(seasons, many=True).data)