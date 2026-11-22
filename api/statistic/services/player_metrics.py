from collections import defaultdict
from django.db.models import Avg, Count, Max, Q, Sum

from game.models import ResultConfig
from league.models import LeagueStanding
from result.models import Result
from user.models import PlayerProfile

from .query_filters import (
    CATEGORY_DEFS,
    DEFAULT_MIN_GAMES,
    DEFAULT_TOP_N,
    DEFAULT_WINDOW,
    _filter_results_by_player_count,
    _filter_standings_by_player_count,
)


def _build_player_pool(years=None, player_counts=None):
    """
    Returns one dict per player who has at least one Result or
    LeagueStanding, merging per-game Result aggregates with per-league
    LeagueStanding aggregates into a single flat set of fields that the
    categories above rank on directly.

    Career fields include the accumulated league points used to rank a
    player's career performance.
    """
    # Results are written before a finishing position is necessarily known.
    # They are not completed games and must not affect player performance.
    result_qs = Result.objects.filter(position__isnull=False)
    if years:
        result_qs = result_qs.filter(season__year__in=years)
    result_qs = _filter_results_by_player_count(result_qs, player_counts)

    result_rows = result_qs.values("player_profile_id").annotate(
        games_played=Count("id"),
        total_wins=Count("id", filter=Q(position=1)),
        avg_position=Avg("position"),
    )

    standing_qs = LeagueStanding.objects.all()
    if years:
        standing_qs = standing_qs.filter(league__season__year__in=years)
    standing_qs = _filter_standings_by_player_count(standing_qs, player_counts)

    standing_rows = standing_qs.values("player_profile_id", "league__level").annotate(
        points=Sum("league_points"),
        cnt=Count("id"),
    )

    pool = {}

    def blank_entry():
        return {
            "games_played": 0,
            "total_wins": 0,
            "avg_position": None,
            "league_points": 0.0,
            "leagues_played": 0,
            "level_points": {},
            "reached_levels": set(),
        }

    for row in result_rows:
        entry = pool.setdefault(row["player_profile_id"], blank_entry())
        entry["games_played"] = row["games_played"] or 0
        entry["total_wins"] = row["total_wins"] or 0
        entry["avg_position"] = (
            float(row["avg_position"]) if row["avg_position"] is not None else None
        )

    for row in standing_rows:
        entry = pool.setdefault(row["player_profile_id"], blank_entry())
        level = row["league__level"]
        points = float(row["points"] or 0)
        if level is not None:
            entry["level_points"][level] = entry["level_points"].get(level, 0.0) + points
            entry["reached_levels"].add(level)
        entry["league_points"] += points
        entry["leagues_played"] += row["cnt"] or 0

    if not pool:
        return []

    profiles = PlayerProfile.objects.filter(id__in=pool.keys()).select_related("user")

    no_points_game_ids = set(
        ResultConfig.objects.filter(has_points=False).values_list("game_id", flat=True)
    )
    record_candidates = result_qs.filter(points__gte=2).exclude(
        selected_game__game_id__in=no_points_game_ids
    )
    game_max_points = (
        record_candidates.values("selected_game__game_id")
        .annotate(max_points=Max("points"))
    )
    game_records_map = {
        row["selected_game__game_id"]: row["max_points"]
        for row in game_max_points
        if row["selected_game__game_id"] is not None
    }
    player_game_records = defaultdict(set)
    if game_records_map:
        for row in record_candidates.values(
            "player_profile_id", "selected_game__game_id", "points"
        ):
            g_id = row["selected_game__game_id"]
            if g_id in game_records_map and row["points"] == game_records_map[g_id]:
                player_game_records[row["player_profile_id"]].add(g_id)

    players = []
    for profile in profiles:
        entry = pool[profile.id]
        games_played = entry["games_played"]
        win_rate = (
            round(entry["total_wins"] / games_played * 100, 1) if games_played > 0 else None
        )
        players.append(
            {
                "profile_id": profile.id,
                "profile_name": profile.profile_name,
                "username": profile.user.username if profile.user else None,
                "games_played": games_played,
                "total_wins": entry["total_wins"],
                "avg_position": (
                    round(entry["avg_position"], 2) if entry["avg_position"] is not None else None
                ),
                "league_points": entry["league_points"],
                "leagues_played": entry["leagues_played"],
                "level_points": entry["level_points"],
                "reached_levels": entry["reached_levels"],
                "records": len(player_game_records.get(profile.id, set())),
                # Human-readable value shown on the career card; ordering is
                # driven separately by the lexicographic key in _rank_career.
                "career_performance": round(entry["league_points"], 2),
                "win_rate": win_rate,
            }
        )
    return players


def _rank_players(players, value_key, better, min_games=None):
    """
    Dense-ranks players by `value_key`: tied players share a rank and the
    next distinct value takes the next rank (matching the dense-rank
    convention already used by `league.models.GameStanding.rank`). Players
    with a None value, or below `min_games` games played, are left out of
    the ranking entirely so a single lucky game can't top a rate-based
    leaderboard.
    """
    eligible = [p for p in players if p.get(value_key) is not None]
    if min_games:
        eligible = [p for p in eligible if p.get("games_played", 0) >= min_games]

    def sort_key(player):
        value = player[value_key]
        primary = -value if better == "higher" else value
        return (primary, player["profile_name"].lower())

    eligible.sort(key=sort_key)

    ranked = []
    rank = 0
    previous_value = object()
    for player in eligible:
        value = player[value_key]
        if value != previous_value:
            rank += 1
            previous_value = value
        ranked.append({**player, "rank": rank, "value": value})
    return ranked


def _rank_career(players):
    """
    Dense-ranks players by total career league points, summed across every
    league they have a standing in. Only players who have actually played a
    league (at least one standing) are ranked; higher total points rank
    higher, with no regard for which league level those points came from.
    """
    eligible = [p for p in players if p.get("leagues_played", 0) > 0]
    return _rank_players(eligible, "career_performance", "higher")


def _rank_iron_will(players, min_games):
    """
    Iron Will: most games played among players at or below the median win
    rate -- a nod to persistence rather than skill. Deliberately ranks (and
    displays) games played, never win rate, so the players who show up here
    are never shown a number that reads as "you're bad at this".
    """
    eligible = [p for p in players if p.get("win_rate") is not None]
    if min_games:
        eligible = [p for p in eligible if p.get("games_played", 0) >= min_games]
    if not eligible:
        return []

    win_rates = sorted(p["win_rate"] for p in eligible)
    mid = len(win_rates) // 2
    median = (
        win_rates[mid]
        if len(win_rates) % 2 == 1
        else (win_rates[mid - 1] + win_rates[mid]) / 2
    )
    below_median = [p for p in eligible if p["win_rate"] <= median]
    return _rank_players(below_median, "games_played", "higher")


def _entry(player, is_me):
    return {
        "rank": player["rank"],
        "value": player["value"],
        # Optional pre-formatted label (e.g. "L1 · 24 pts" for the career
        # metric); the card shows it verbatim when present.
        "display": player.get("display"),
        # Highest league reached (career metric), so the card can render a
        # proper league badge instead of the "L1" text baked into `display`.
        "best_level": player.get("best_level"),
        "profile_id": player["profile_id"],
        "profile_name": player["profile_name"],
        "username": player["username"],
        "is_me": is_me,
        "eligible": True,
    }


def _unranked_me_entry(profile, raw_value):
    return {
        "rank": None,
        "value": raw_value,
        "display": None,
        "best_level": None,
        "profile_id": profile.id,
        "profile_name": profile.profile_name,
        "username": profile.user.username if profile.user else None,
        "is_me": True,
        "eligible": False,
    }


def get_statistics_overview(
    profile,
    years=None,
    player_counts=None,
    min_games=DEFAULT_MIN_GAMES,
    window=DEFAULT_WINDOW,
    top_n=DEFAULT_TOP_N,
):
    """
    Builds, for every category in CATEGORY_DEFS, the top N players plus a
    window of players surrounding `profile`'s own rank, so a player can
    always see the best players AND exactly where they themselves stand --
    even if they don't have enough games played to be formally ranked.
    """
    from .awards import get_awards

    players = _build_player_pool(years=years, player_counts=player_counts)
    me_raw = next((p for p in players if p["profile_id"] == profile.id), None)

    categories = []
    for definition in CATEGORY_DEFS:
        custom = definition.get("custom")
        if custom == "career":
            threshold = None
            ranked = _rank_career(players)
        elif custom == "iron_will":
            threshold = min_games
            ranked = _rank_iron_will(players, min_games)
        else:
            threshold = min_games if definition["rate_based"] else None
            ranked = _rank_players(
                players, definition["key"], definition["better"], min_games=threshold
            )

        top = [_entry(p, p["profile_id"] == profile.id) for p in ranked[:top_n]]

        me_index = next((i for i, p in enumerate(ranked) if p["profile_id"] == profile.id), None)
        if me_index is not None:
            lo = max(0, me_index - window)
            hi = min(len(ranked), me_index + window + 1)
            around_me = [_entry(p, p["profile_id"] == profile.id) for p in ranked[lo:hi]]
            me_summary = around_me[me_index - lo]
        else:
            around_me = []
            # Iron Will isn't a raw pool field (it's a derived ranking), so
            # an unranked player's "so far" value falls back to the field
            # it's actually ranked and displayed by: games played.
            if custom == "iron_will":
                raw_value = me_raw["games_played"] if me_raw else 0
            else:
                raw_value = me_raw.get(definition["key"]) if me_raw else 0
            me_summary = _unranked_me_entry(profile, raw_value)

        categories.append(
            {
                "key": definition["key"],
                "label": definition["label"],
                "description": definition["description"],
                "unit": definition["unit"],
                "better": definition["better"],
                "min_games": threshold,
                "total_ranked": len(ranked),
                "me": me_summary,
                "top": top,
                "around_me": around_me,
            }
        )

    return {
        "min_games": min_games,
        "window": window,
        "categories": categories,
        "awards": get_awards(
            profile, years=years, player_counts=player_counts, top_n=top_n, window=window
        ),
    }
