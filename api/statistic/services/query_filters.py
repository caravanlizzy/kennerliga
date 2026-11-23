from django.db.models import Count, IntegerField, OuterRef, Subquery

from league.models import LeagueStanding
from result.models import Result

DEFAULT_MIN_GAMES = 0
# One player above and one below the requesting player, per the statistics
# dashboard spec ("with a player above and below").
DEFAULT_WINDOW = 1
DEFAULT_TOP_N = 5
DEFAULT_GAME_MIN_GAMES = 0
# Podium size for the "most picked"/"most banned" games shown atop the games
# statistics section.
DEFAULT_POPULAR_GAMES_N = 3

# Fun "superlative" awards: ranked the same way as the categories below (no
# min-games gate, since these are lighthearted counts rather than skill
# rankings) so they can share the same card -- top N, an "around me" window,
# and a highlighted own-rank row. Each definition's `key` matches the award
# key returned by `get_awards`.
AWARD_DEFS = [
    {
        "key": "hater",
        "label": "Hater",
        "description": "Most bans.",
        "unit": "",
    },
    {
        "key": "inspirer",
        "label": "Inspiration",
        "description": "Most different picks.",
        "unit": "",
    },
    {
        "key": "spammer",
        "label": "Spammer",
        "description": "Most picks of the same game.",
        "unit": "",
    },
]

# Each category key must match a key present in the player dicts built by
# `_build_player_pool`. `rate_based` categories only make sense with a
# minimum sample size (win rate/avg position on 1 game is noise), so a
# `min_games` threshold is applied to them before ranking. The category
# flagged `custom` is ranked by the dedicated ranker in `_rank_career`.
CATEGORY_DEFS = [
    {
        "key": "career_performance",
        "label": "Career League Points",
        "description": "Total league points earned across all leagues.",
        "unit": "pts",
        "better": "higher",
        "rate_based": False,
        "custom": "career",
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
    {
        "key": "records",
        "label": "Most Records",
        "description": "Most game high-score records held.",
        "unit": "",
        "better": "higher",
        "rate_based": False,
    },
    {
        "key": "iron_will",
        "label": "Iron Will",
        "description": "Most games played among players below the median win rate -- keeps showing up, game after game.",
        "unit": "",
        "better": "higher",
        "rate_based": False,
        "custom": "iron_will",
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
    of `player_counts`, using a grouped aggregation subquery.
    """
    if not player_counts:
        return qs
    matching_sg_ids = (
        Result.objects.values("selected_game_id")
        .annotate(cnt=Count("id"))
        .filter(cnt__in=player_counts)
        .values("selected_game_id")
    )
    return qs.filter(selected_game_id__in=matching_sg_ids)


def _filter_standings_by_player_count(qs, player_counts):
    """
    Restricts a queryset whose model has a direct `league` FK (e.g.
    `LeagueStanding`, `BanDecision`, `SelectedGame`) to leagues whose size
    (number of standings) is one of `player_counts`, using a grouped aggregation subquery.
    """
    if not player_counts:
        return qs
    matching_league_ids = (
        LeagueStanding.objects.values("league_id")
        .annotate(cnt=Count("id"))
        .filter(cnt__in=player_counts)
        .values("league_id")
    )
    return qs.filter(league_id__in=matching_league_ids)
