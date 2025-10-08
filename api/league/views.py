from collections import defaultdict
from decimal import Decimal

from django.db.models import Prefetch, Window, Max, F, Case, When, IntegerField, Sum, OuterRef, Subquery
from django.db.models import prefetch_related_objects
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from game.models import SelectedGame, BanDecision
from league.models import League
from league.serializer import LeagueSerializer, LeagueDetailSerializer
from result.models import Result
from result.serializers import ResultSerializer


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

    from collections import defaultdict
    from decimal import Decimal
    from rest_framework.response import Response

    # place -> league points
    PLACE_POINTS = {1: Decimal("6"), 2: Decimal("3"), 3: Decimal("1"), 4: Decimal("0")}

    @action(detail=True, methods=['get'], url_path='result-summary')
    def results(self, request, pk=None):
        # Fetch minimal fields; no window functions, works on SQLite
        qs = (
            Result.objects
            .filter(league_id=pk)
            .select_related('selected_game', 'player_profile')
            .only('id', 'points', 'selected_game_id', 'player_profile_id', 'player_profile__profile_name')
        )

        # Group results by selected_game
        by_game: dict[int, list] = defaultdict(list)
        for r in qs:
            by_game[r.selected_game_id].append(r)

        # Per-player totals
        totals = {}  # player_id -> dict

        def ensure(pid, name):
            if pid not in totals:
                totals[pid] = {
                    "player": name,
                    "player_id": pid,
                    "wins": Decimal("0"),
                    "league_points": Decimal("0")
                }

        for game_id, results in by_game.items():
            # sort by raw points desc
            results.sort(key=lambda x: x.points, reverse=True)

            # group by score to detect ties
            i = 0
            place = 1
            n = len(results)
            while i < n:
                # collect tie block with same points
                j = i + 1
                while j < n and results[j].points == results[i].points:
                    j += 1
                block = results[i:j]  # tied players
                block_size = len(block)

                # sum points for occupied places, then split
                occupied_places = range(place, place + block_size)
                total_for_places = sum(self.PLACE_POINTS.get(p, Decimal("0")) for p in occupied_places)
                share = (total_for_places / block_size) if block_size else Decimal("0")

                # determine if this block is "top" -> counts as a win (ties count as wins)
                is_top_block = (place == 1)

                # assign to players
                for r in block:
                    ensure(r.player_profile_id, r.player_profile.profile_name)
                    totals[r.player_profile_id]["league_points"] += share
                    if is_top_block:
                        totals[r.player_profile_id]["wins"] += Decimal("1")  # ties count as wins

                # advance
                place += block_size
                i = j

        # shape + sort
        data = list(totals.values())
        data.sort(key=lambda row: (-row["league_points"], -row["wins"], row["player"]))

        # Convert Decimals to float for JSON, if you prefer
        for row in data:
            row["league_points"] = float(row["league_points"])
            row["wins"] = float(row["wins"])

        return Response(data)


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
