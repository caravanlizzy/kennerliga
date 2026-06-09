"""
Helpers to build scoreboard payloads for a whole season in a small number of
queries.

The previous implementation ran, *per league*, one extra members query plus
one ``GameStanding`` query and one ``LeagueStanding`` query. For a season with
N leagues that is roughly ``3 * N`` queries on top of the league fetch.

This module loads ``GameStanding`` and ``LeagueStanding`` rows for the whole
season **once**, groups them by ``league_id`` in Python, and then composes
per-league payloads using the already-prefetched ``league.members``.

Public API:

* :func:`build_season_scoreboards` -> list[dict], one payload per league
* :func:`build_league_scoreboard_payload` -> single-league payload (kept for
  backward compatibility; now accepts optional pre-grouped data)
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from league.models import GameStanding, League, LeagueStanding


def _members_from_league(league: League) -> tuple[List[int], Dict[int, str]]:
    """
    Extract ``(player_order, player_names)`` from a league whose ``members``
    relation has already been prefetched with ``select_related('profile__user')``
    and ordered by ``rank, id``.

    Falls back to a ``.values()`` query if the prefetch is missing.
    """
    cached = getattr(league, "_prefetched_objects_cache", None)
    if cached is not None and "members" in cached:
        members = list(cached["members"])
        player_order = [m.profile_id for m in members]
        player_names = {
            m.profile_id: getattr(m.profile, "profile_name", f"Player {m.profile_id}")
            for m in members
        }
        return player_order, player_names

    # Fallback: shouldn't happen on hot paths, but keep correctness.
    rows = list(
        league.members.select_related("profile__user")
        .order_by("rank", "id")
        .values("profile", "profile__profile_name")
    )
    return (
        [r["profile"] for r in rows],
        {r["profile"]: r["profile__profile_name"] for r in rows},
    )


def build_league_scoreboard_payload(
    league: League,
    game_standings: Optional[Iterable[GameStanding]] = None,
    league_standings: Optional[Iterable[LeagueStanding]] = None,
) -> dict:
    """
    Compose a grid-friendly scoreboard payload for a single league.

    If ``game_standings`` / ``league_standings`` are provided, they are used
    as-is (already filtered to this league). Otherwise they are loaded from
    the DB — kept as a fallback for callers that still pass a bare league.
    """
    player_order, player_names = _members_from_league(league)

    if game_standings is None:
        game_standings = (
            GameStanding.objects.filter(league=league.id)
            .select_related("player_profile", "selected_game__game")
            .order_by("selected_game_id", "rank")
        )

    by_game: Dict[int, list] = defaultdict(list)
    game_meta: Dict[int, dict] = {}
    for row in game_standings:
        by_game[row.selected_game_id].append(row)
        if row.selected_game_id not in game_meta:
            game_meta[row.selected_game_id] = {
                "game_name": getattr(
                    row.selected_game.game, "name", str(row.selected_game.game)
                )
            }

    columns = ["Game"] + [
        player_names.get(pid, f"Player {pid}") for pid in player_order
    ]

    rows: List[dict] = []
    for selected_game_id, standings in by_game.items():
        points_by_player = {
            s.player_profile_id: getattr(s, "ingame_points", None) for s in standings
        }
        cells = [
            {
                "player_id": pid,
                "profile_name": player_names.get(pid, f"Player {pid}"),
                "value": points_by_player.get(pid),
                "display": (
                    f"{points_by_player.get(pid)} pts"
                    if points_by_player.get(pid) is not None
                    else "—"
                ),
            }
            for pid in player_order
        ]
        rows.append(
            {
                "type": "game",
                "selected_game_id": selected_game_id,
                "game": game_meta[selected_game_id]["game_name"],
                "cells": cells,
            }
        )

    if league_standings is None:
        league_standings = LeagueStanding.objects.filter(
            league=league.id
        ).select_related("player_profile")

    league_points_by_player = {
        ls.player_profile_id: getattr(ls, "league_points", 0) for ls in league_standings
    }
    total_cells = [
        {
            "player_id": pid,
            "profile_name": player_names.get(pid, f"Player {pid}"),
            "value": league_points_by_player.get(pid, 0),
            "display": f"{league_points_by_player.get(pid, 0)} pts",
        }
        for pid in player_order
    ]
    rows.append(
        {"type": "league_totals", "label": "League Points", "cells": total_cells}
    )

    return {
        "league": {"id": league.id, "name": league.level},
        "columns": columns,
        "rows": rows,
    }


def build_season_scoreboards(leagues: Iterable[League]) -> List[dict]:
    """
    Build scoreboard payloads for every league in ``leagues`` using only two
    extra queries total (one ``GameStanding`` query + one ``LeagueStanding``
    query for the whole set), regardless of how many leagues there are.

    ``leagues`` is expected to be an already-evaluated iterable (list) whose
    ``members`` relation has been prefetched and ordered by ``rank, id``.
    """
    leagues = list(leagues)
    if not leagues:
        return []

    league_ids = [l.id for l in leagues]

    gs_rows = (
        GameStanding.objects.filter(league_id__in=league_ids)
        .select_related("selected_game__game")
        .order_by("league_id", "selected_game_id", "rank")
    )
    gs_by_league: Dict[int, list] = defaultdict(list)
    for row in gs_rows:
        gs_by_league[row.league_id].append(row)

    ls_rows = LeagueStanding.objects.filter(league_id__in=league_ids)
    ls_by_league: Dict[int, list] = defaultdict(list)
    for row in ls_rows:
        ls_by_league[row.league_id].append(row)

    return [
        build_league_scoreboard_payload(
            league,
            game_standings=gs_by_league.get(league.id, []),
            league_standings=ls_by_league.get(league.id, []),
        )
        for league in leagues
    ]
