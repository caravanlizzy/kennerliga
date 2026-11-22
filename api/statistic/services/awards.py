from collections import defaultdict

from django.db.models import Count

from game.models import BanDecision, SelectedGame
from game.queries import get_successfully_banned_game_ids
from user.models import PlayerProfile

from .player_metrics import _entry, _rank_players, _unranked_me_entry
from .query_filters import (
    AWARD_DEFS,
    DEFAULT_TOP_N,
    DEFAULT_WINDOW,
    _filter_standings_by_player_count,
)


def get_awards(
    profile, years=None, player_counts=None, top_n=DEFAULT_TOP_N, window=DEFAULT_WINDOW
):
    """
    Builds the fun "superlative" awards: the Hater (most games banned, where
    skipping a ban doesn't count), the Inspirer (most different games picked
    across leagues -- only non-banned picks count, with at most 1 game per
    league), and the Spammer (the most times any single player has picked
    the *same* game across leagues). Ranked the same way as the categories in
    `get_statistics_overview` -- dense rank, top N plus a window around the
    requesting player -- so they render through the same card.
    """
    ban_qs = BanDecision.objects.filter(skipped_ban=False, selected_game__isnull=False)
    if years:
        ban_qs = ban_qs.filter(league__season__year__in=years)
    ban_qs = _filter_standings_by_player_count(ban_qs, player_counts)
    ban_rows = list(
        ban_qs.values("player_banning_id").annotate(value=Count("id")).order_by()
    )

    banned_sg_ids = get_successfully_banned_game_ids(years=years)
    pick_qs = SelectedGame.objects.exclude(id__in=banned_sg_ids)
    if years:
        pick_qs = pick_qs.filter(league__season__year__in=years)
    pick_qs = _filter_standings_by_player_count(pick_qs, player_counts)
    pick_rows = list(
        pick_qs.values("profile_id").annotate(value=Count("game_id", distinct=True)).order_by()
    )

    # Per player, per game, how many times that game was picked -- the
    # Spammer's value is each player's own most-repeated game.
    pick_by_game_rows = list(
        pick_qs.values("profile_id", "game__name").annotate(value=Count("id")).order_by()
    )
    rows_by_profile = defaultdict(list)
    for row in pick_by_game_rows:
        rows_by_profile[row["profile_id"]].append(row)
    most_repeated_pick = {
        pid: min(rows, key=lambda r: (-r["value"], r["game__name"].lower()))
        for pid, rows in rows_by_profile.items()
    }

    profile_ids = {row["player_banning_id"] for row in ban_rows} | {
        row["profile_id"] for row in pick_rows
    }
    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(id__in=profile_ids).select_related("user")
    }

    def players_from_counts(value_by_id, display_by_id=None):
        return [
            {
                "profile_id": pid,
                "profile_name": player.profile_name,
                "username": player.user.username if player.user else None,
                "value": value_by_id[pid],
                "display": (display_by_id or {}).get(pid),
            }
            for pid, player in profile_map.items()
            if pid in value_by_id
        ]

    def rank_award(players, value_by_id):
        ranked = _rank_players(players, "value", "higher")

        top = [_entry(p, p["profile_id"] == profile.id) for p in ranked[:top_n]]

        me_index = next((i for i, p in enumerate(ranked) if p["profile_id"] == profile.id), None)
        if me_index is not None:
            lo = max(0, me_index - window)
            hi = min(len(ranked), me_index + window + 1)
            around_me = [_entry(p, p["profile_id"] == profile.id) for p in ranked[lo:hi]]
            me_summary = around_me[me_index - lo]
        else:
            around_me = []
            me_summary = _unranked_me_entry(profile, value_by_id.get(profile.id, 0))

        return top, around_me, me_summary, len(ranked)

    ban_value_by_id = {row["player_banning_id"]: row["value"] for row in ban_rows}
    pick_value_by_id = {row["profile_id"]: row["value"] for row in pick_rows}
    spam_value_by_id = {pid: row["value"] for pid, row in most_repeated_pick.items()}
    spam_display_by_id = {
        pid: f'{row["value"]}x {row["game__name"]}' for pid, row in most_repeated_pick.items()
    }

    rankings_by_key = {
        "hater": rank_award(players_from_counts(ban_value_by_id), ban_value_by_id),
        "inspirer": rank_award(players_from_counts(pick_value_by_id), pick_value_by_id),
        "spammer": rank_award(
            players_from_counts(spam_value_by_id, spam_display_by_id), spam_value_by_id
        ),
    }

    awards = []
    for definition in AWARD_DEFS:
        top, around_me, me_summary, total_ranked = rankings_by_key[definition["key"]]
        awards.append(
            {
                "key": definition["key"],
                "label": definition["label"],
                "description": definition["description"],
                "unit": definition["unit"],
                "better": "higher",
                "min_games": None,
                "total_ranked": total_ranked,
                "me": me_summary,
                "top": top,
                "around_me": around_me,
            }
        )
    return awards
