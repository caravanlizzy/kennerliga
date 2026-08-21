"""
Aggregation and ranking logic backing the player/game statistics dashboard.

This module intentionally owns no models of its own: it only reads from
`result.Result` and `league.LeagueStanding`, which already hold all the raw
data a player-facing statistics page needs. Keeping the logic here (rather
than on the models or in the view) mirrors the separation already used by
`user.service.get_user_summary_stats`.
"""
from django.db.models import (
    Avg,
    Count,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
)

from game.models import BanDecision, SelectedGame
from league.models import LeagueStanding
from result.models import Result
from user.models import PlayerProfile

DEFAULT_MIN_GAMES = 3
# One player above and one below the requesting player, per the statistics
# dashboard spec ("with a player above and below").
DEFAULT_WINDOW = 1
DEFAULT_TOP_N = 5
DEFAULT_GAME_MIN_GAMES = 2
DEFAULT_AWARD_TOP_N = 3

# Fun "superlative" awards: a fixed top-N podium rather than a full ranking
# (no min-games gate or "around me" window -- these are lighthearted counts,
# not skill rankings). Each definition's `key` matches the award key
# returned by `get_awards`.
AWARD_DEFS = [
    {
        "key": "hater",
        "label": "Hater",
        "description": "Most games banned (skipping a ban doesn't count).",
        "unit": "bans",
    },
    {
        "key": "inspirer",
        "label": "Inspirer",
        "description": "Most different games picked for a league.",
        "unit": "games",
    },
]

# Each category key must match a key present in the player dicts built by
# `_build_player_pool`. `rate_based` categories only make sense with a
# minimum sample size (win rate/avg position on 1 game is noise), so a
# `min_games` threshold is applied to them before ranking. The category
# flagged `custom` is not ranked by a single numeric field but by the
# dedicated lexicographic ranker in `_rank_career`.
CATEGORY_DEFS = [
    {
        "key": "career_performance",
        "label": "Career League Performance",
        "description": "Highest league you've reached, with total league points as a tie-break - any L1 result outranks every lower league.",
        "unit": "pts",
        "better": "higher",
        "rate_based": False,
        "custom": True,
    },
    {
        "key": "win_rate",
        "label": "Win Rate",
        "description": "Percentage of played games won.",
        "unit": "%",
        "better": "higher",
        "rate_based": True,
    },
    {
        "key": "avg_position",
        "label": "Average Position",
        "description": "Average finishing position across all games (lower is better).",
        "unit": "",
        "better": "lower",
        "rate_based": True,
    },
    {
        "key": "games_played",
        "label": "Games Played",
        "description": "Total number of games played.",
        "unit": "",
        "better": "higher",
        "rate_based": False,
    },
]


def parse_years(raw):
    """
    Accepts a comma-separated string, list/tuple/set of ints/strings, or
    None, and returns a list of ints (or None if nothing usable was found).
    Mirrors the `years` parsing already used by `user.views.user_statistics`.
    """
    if not raw:
        return None
    tokens = raw.split(",") if isinstance(raw, str) else raw
    years = [int(str(token).strip()) for token in tokens if str(token).strip().isdigit()]
    return years or None


def parse_player_counts(raw):
    """
    Accepts a comma-separated string (e.g. "4p,3p"), a list/tuple/set, a
    single value, or None, and returns a list of ints (2/3/4/...) or None.
    Mirrors the `player_count` parsing used by `user.views.user_statistics`,
    where filters look like the ones on the players list.
    """
    if not raw:
        return None
    if isinstance(raw, str):
        if raw.strip().lower() == "all":
            return None
        tokens = raw.split(",")
    elif isinstance(raw, (list, tuple, set)):
        tokens = list(raw)
    else:
        tokens = [raw]

    counts = []
    for token in tokens:
        cleaned = str(token).lower().replace("p", "").strip()
        if cleaned.isdigit():
            counts.append(int(cleaned))
    return counts or None


def _filter_results_by_player_count(qs, player_counts):
    """
    Restricts a `Result` queryset to matches whose participant count is one
    of `player_counts`, using the same per-`selected_game` participant-count
    subquery that `user.service.get_user_summary_stats` relies on.
    """
    if not player_counts:
        return qs
    subquery = (
        Result.objects.filter(selected_game=OuterRef("selected_game"))
        .order_by()
        .values("selected_game")
        .annotate(cnt=Count("id"))
        .values("cnt")
    )
    return qs.annotate(
        match_player_count=Subquery(subquery, output_field=IntegerField())
    ).filter(match_player_count__in=player_counts)


def _filter_standings_by_player_count(qs, player_counts):
    """
    Restricts a queryset whose model has a direct `league` FK (e.g.
    `LeagueStanding`, `BanDecision`, `SelectedGame`) to leagues whose size
    (number of standings) is one of `player_counts`, so career/ban/pick
    metrics all respect the same player-count filter as the per-game
    aggregates.
    """
    if not player_counts:
        return qs
    subquery = (
        LeagueStanding.objects.filter(league=OuterRef("league"))
        .order_by()
        .values("league")
        .annotate(cnt=Count("id"))
        .values("cnt")
    )
    return qs.annotate(
        league_size=Subquery(subquery, output_field=IntegerField())
    ).filter(league_size__in=player_counts)


def _build_player_pool(years=None, player_counts=None):
    """
    Returns one dict per player who has at least one Result or
    LeagueStanding, merging per-game Result aggregates with per-league
    LeagueStanding aggregates into a single flat set of fields that the
    categories above rank on directly.

    Career fields (`level_points`, `reached_levels`, `career_performance`)
    capture, per league level, how far the player has climbed so the
    lexicographic career ranker in `_rank_career` can favour higher leagues.
    """
    result_qs = Result.objects.all()
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


def _format_points(points):
    """Formats league points without a trailing ".0" (e.g. 24 not 24.0)."""
    rounded = round(float(points), 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:g}"


def _rank_career(players):
    """
    Dense-ranks players by career *league performance* using a strict
    lexicographic comparison across league levels: L1 achievement dominates
    L2, which dominates L3, and so on. Merely participating in a level
    (having any standing there) already outranks anyone who never reached
    it; within the same level, accumulated league points break the tie
    before falling through to the next level. The displayed value is a
    readable label -- the highest league reached plus total league points,
    e.g. "L1 \u00b7 24 pts" -- so the shown number always agrees with the
    highest-league-first ranking instead of a bare points total.
    """
    eligible = [p for p in players if p.get("leagues_played", 0) > 0]
    if not eligible:
        return []

    levels = sorted({lvl for p in eligible for lvl in p["reached_levels"]})

    def sort_key(player):
        components = []
        for level in levels:
            reached = 1 if level in player["reached_levels"] else 0
            points = player["level_points"].get(level, 0.0)
            # Negated so "reached" and higher points sort first (better).
            components.append(-reached)
            components.append(-points)
        components.append(player["profile_name"].lower())
        return tuple(components)

    def tie_key(player):
        return tuple(
            (1 if level in player["reached_levels"] else 0, player["level_points"].get(level, 0.0))
            for level in levels
        )

    eligible.sort(key=sort_key)

    ranked = []
    rank = 0
    previous_key = object()
    for player in eligible:
        key = tie_key(player)
        if key != previous_key:
            rank += 1
            previous_key = key
        # Highest league reached is the smallest level number (L1 is top).
        # The card shows this as the primary metric ("L1"), with total
        # league points as a readable detail ("L1 · 24 pts"), so the number
        # on the card always matches the highest-league-first ranking.
        best_level = min(player["reached_levels"])
        points = player["career_performance"]
        display = f"L{best_level} · {_format_points(points)} pts"
        ranked.append(
            {
                **player,
                "rank": rank,
                "value": player["career_performance"],
                "best_level": best_level,
                "display": display,
            }
        )
    return ranked


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
    players = _build_player_pool(years=years, player_counts=player_counts)
    me_raw = next((p for p in players if p["profile_id"] == profile.id), None)

    categories = []
    for definition in CATEGORY_DEFS:
        if definition.get("custom"):
            threshold = None
            ranked = _rank_career(players)
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
            raw_value = me_raw[definition["key"]] if me_raw else None
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
        "awards": get_awards(profile, years=years, player_counts=player_counts),
    }


def get_awards(profile, years=None, player_counts=None, top_n=DEFAULT_AWARD_TOP_N):
    """
    Builds the fun "superlative" awards podiums: the Hater (most games
    banned, where skipping a ban doesn't count) and the Inspirer (most
    different games picked for a league). Unlike the ranked categories
    above, these are a fixed top-N with no min-games gate or "around me"
    window -- just a lighthearted leaderboard.
    """
    ban_qs = BanDecision.objects.filter(skipped_ban=False, selected_game__isnull=False)
    if years:
        ban_qs = ban_qs.filter(league__season__year__in=years)
    ban_qs = _filter_standings_by_player_count(ban_qs, player_counts)
    ban_rows = list(
        ban_qs.values("player_banning_id").annotate(value=Count("id")).order_by()
    )

    pick_qs = SelectedGame.objects.all()
    if years:
        pick_qs = pick_qs.filter(league__season__year__in=years)
    pick_qs = _filter_standings_by_player_count(pick_qs, player_counts)
    pick_rows = list(
        pick_qs.values("profile_id")
        .annotate(value=Count("game", distinct=True))
        .order_by()
    )

    profile_ids = {row["player_banning_id"] for row in ban_rows} | {
        row["profile_id"] for row in pick_rows
    }
    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(id__in=profile_ids).select_related("user")
    }

    def top_entries(rows, id_key):
        named = [(row, profile_map[row[id_key]]) for row in rows if row[id_key] in profile_map]
        named.sort(key=lambda pair: (-pair[0]["value"], pair[1].profile_name.lower()))
        return [
            {
                "profile_id": player.id,
                "profile_name": player.profile_name,
                "value": row["value"],
                "is_me": player.id == profile.id,
            }
            for row, player in named[:top_n]
        ]

    entries_by_key = {
        "hater": top_entries(ban_rows, "player_banning_id"),
        "inspirer": top_entries(pick_rows, "profile_id"),
    }

    return [
        {**definition, "top3": entries_by_key[definition["key"]]}
        for definition in AWARD_DEFS
    ]


def list_games_with_stats(years=None, player_counts=None):
    """
    Returns every game that has at least one recorded result, with basic
    popularity stats, for use as a picker for the per-game leaderboard.
    """
    qs = Result.objects.select_related("selected_game__game__platform")
    if years:
        qs = qs.filter(season__year__in=years)
    qs = _filter_results_by_player_count(qs, player_counts)

    rows = (
        qs.values(
            "selected_game__game_id",
            "selected_game__game__name",
            "selected_game__game__platform__name",
        )
        .annotate(
            games_played=Count("id"),
            distinct_players=Count("player_profile", distinct=True),
        )
        .order_by("-games_played", "selected_game__game__name")
    )

    return [
        {
            "game_id": row["selected_game__game_id"],
            "name": row["selected_game__game__name"],
            "platform": row["selected_game__game__platform__name"],
            "games_played": row["games_played"],
            "distinct_players": row["distinct_players"],
        }
        for row in rows
        if row["selected_game__game_id"] is not None
    ]


def get_game_leaderboard(
    game, profile, years=None, player_counts=None, min_games=DEFAULT_GAME_MIN_GAMES
):
    """
    Ranks every player who has played `game`, ordered by win rate (desc)
    then average position (asc) as a tie-break -- the same "most wins, then
    most consistent" ordering already used to pick a player's `top_games` in
    `user.views.UserViewSet.user_statistics`. Players below `min_games` are
    excluded from the ranking (too few games to mean anything) but the
    requesting player's own row is always returned separately via `me`.
    """
    qs = Result.objects.filter(selected_game__game=game)
    if years:
        qs = qs.filter(season__year__in=years)
    qs = _filter_results_by_player_count(qs, player_counts)

    rows = qs.values("player_profile_id").annotate(
        games_played=Count("id"),
        wins=Count("id", filter=Q(position=1)),
        avg_position=Avg("position"),
    )

    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(
            id__in=[row["player_profile_id"] for row in rows]
        ).select_related("user")
    }

    players = []
    for row in rows:
        p = profile_map.get(row["player_profile_id"])
        if not p:
            continue
        played = row["games_played"] or 0
        wins = row["wins"] or 0
        players.append(
            {
                "profile_id": p.id,
                "profile_name": p.profile_name,
                "username": p.user.username if p.user else None,
                "games_played": played,
                "wins": wins,
                "avg_position": (
                    round(float(row["avg_position"]), 2)
                    if row["avg_position"] is not None
                    else None
                ),
                "win_rate": round(wins / played * 100, 1) if played > 0 else None,
            }
        )

    eligible = [p for p in players if p["games_played"] >= min_games]
    excluded_low_sample_count = len(players) - len(eligible)

    def sort_key(player):
        return (
            -(player["win_rate"] or 0),
            player["avg_position"] if player["avg_position"] is not None else float("inf"),
            -player["games_played"],
            player["profile_name"].lower(),
        )

    eligible.sort(key=sort_key)

    leaderboard = []
    rank = 0
    previous_key = None
    for player in eligible:
        key = (player["win_rate"], player["avg_position"])
        if key != previous_key:
            rank += 1
            previous_key = key
        leaderboard.append(
            {
                **player,
                "rank": rank,
                "is_me": player["profile_id"] == profile.id,
                "eligible": True,
            }
        )

    me_entry = next((row for row in leaderboard if row["profile_id"] == profile.id), None)
    if me_entry is None:
        raw = next((p for p in players if p["profile_id"] == profile.id), None)
        me_entry = {
            **(raw or {
                "profile_id": profile.id,
                "profile_name": profile.profile_name,
                "username": profile.user.username if profile.user else None,
                "games_played": 0,
                "wins": 0,
                "avg_position": None,
                "win_rate": None,
            }),
            "rank": None,
            "is_me": True,
            "eligible": False,
        }

    return {
        "game_id": game.id,
        "name": game.name,
        "platform": game.platform.name,
        "min_games": min_games,
        "excluded_low_sample_count": excluded_low_sample_count,
        "leaderboard": leaderboard,
        "me": me_entry,
    }
