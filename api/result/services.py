from django.db import transaction
from result.models import Result
from game.models import Faction, TieBreaker
from league.models import LeagueStatus, GameStanding
from league.queries import is_league_finished
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot
from .serializers import ResultSerializer
from league.serializer import GameStandingSerializer

def finalize_results(serializers, rows, base_field, use_points, tbs, selected_game, league, decisive_tb=None, needing_pids=None):
    if needing_pids is None:
        needing_pids = set()

    def fnum(x, default=None):
        try:
            return float(x)
        except (TypeError, ValueError):
            return default

    def get_full_sort_key(row):
        base_val = fnum(row.get(base_field), 0)
        key = [-base_val] if use_points else [base_val]
        for tb in tbs:
            val = fnum(row.get("tie_breaker_value"))
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

        if league.is_finished:
            league.status = LeagueStatus.DONE
            league.save(update_fields=["status"])

    return saved

def get_game_standings_data(league, selected_game_id):
    standings = GameStanding.objects.filter(
        league=league, 
        selected_game_id=selected_game_id
    ).select_related("player_profile").order_by("rank", "player_profile__profile_name")
    return GameStandingSerializer(standings, many=True).data

def get_tie_groups(rows, base_field, use_points, tbs, level):
    """
    Returns a list of 'tie groups' (lists of result dicts).
    A group is a tie if its size > 1.
    'level' is the index in 'tbs' we have reached.
    If level == -1, we only check the base_field.
    If level >= 0, we check base_field AND tbs[0...level].
    """
    def fnum(x, default=None):
        try:
            return float(x)
        except (TypeError, ValueError):
            return default

    def key_up_to(row, lvl):
        # We want to group by base_field AND all tbs up to lvl
        # If use_points is true, higher is better, so we can't just group by value?
        # Actually, grouping just needs equality.
        key = [row.get(base_field)]
        for i in range(lvl + 1):
            tb = tbs[i]
            val = fnum(row.get("tie_breaker_value")) if i == lvl else fnum(row.get(f"tb_{tb.id}"))
            # Note: the view logic seems to assume 'tie_breaker_value' is the one currently being submitted.
            # This is a bit tricky if we have multiple levels of ties.
            key.append(val)
        return tuple(key)

    groups_map = {}
    for r in rows:
        k = key_up_to(r, level)
        if k not in groups_map:
            groups_map[k] = []
        groups_map[k].append(r)

    return [g for g in groups_map.values() if len(g) > 1]
