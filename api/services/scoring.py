from __future__ import annotations


from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Literal

# Public row DTO you pass into the scorer
@dataclass(frozen=True)
class Row:
    selected_game_id: int
    player_id: int
    player_name: str
    points: Decimal | int | float  # raw match points
    position: int | None = None    # rank/position from the game

# Default place->league points mapping (edit as needed)
DEFAULT_PLACE_POINTS: Dict[int, Decimal] = {
    1: Decimal("6"),
    2: Decimal("3"),
    3: Decimal("1"),
    4: Decimal("0"),
}

WinMode = Literal["count_top_block", "fractional", "single"]


def compute_league_table(
    rows: Iterable[Row],
    place_points: Dict[int, Decimal] = DEFAULT_PLACE_POINTS,
    win_mode: WinMode = "count_top_block",
    return_decimals: bool = False,
) -> List[Dict]:
    """
    Aggregate across all selected_games to produce league standings.

    Rules:
      - Dense rank by raw points *within each selected_game*.
      - Ties share the sum of occupied places' league points (e.g., tie for 1st of two players => (6+3)/2=4.5 each).
      - win_mode:
          - "count_top_block": everyone in the top block gets 1 win.
          - "fractional": top block shares 1.0 wins evenly.
          - "single": exactly one win (first within the top block in sorted order).

    Returns a list of dicts sorted by (-league_points, -wins, -points, player).
      Dict keys: player, player_id, points, wins, league_points
    """
    by_game: Dict[int, List[Row]] = defaultdict(list)
    for r in rows:
        by_game[r.selected_game_id].append(r)

    totals: Dict[int, Dict] = {}

    def ensure(pid: int, name: str):
        if pid not in totals:
            totals[pid] = {
                "player": name,
                "player_id": pid,
                "points": Decimal("0"),
                "wins": Decimal("0"),
                "league_points": Decimal("0"),
            }

    for game_id, lst in by_game.items():
        per_game = _dense_rank_and_share(lst, place_points, win_mode)
        for entry in per_game:
            ensure(entry["player_id"], entry["player"])
            totals[entry["player_id"]]["points"] += entry["points"]
            totals[entry["player_id"]]["league_points"] += entry["league_points"]
            totals[entry["player_id"]]["wins"] += entry["wins"]

    out = list(totals.values())
    out.sort(key=lambda r: (-r["league_points"], -r["wins"], -r["points"], r["player"]))

    if not return_decimals:
        for r in out:
            r["points"] = float(r["points"])
            r["league_points"] = float(r["league_points"])
            r["wins"] = float(r["wins"])
    return out


def compute_game_breakdown(
    rows: Iterable[Row],
    place_points: Dict[int, Decimal] = DEFAULT_PLACE_POINTS,
    win_mode: WinMode = "count_top_block",
    return_decimals: bool = False,
) -> List[Dict]:
    """
    Compute the per-selected_game breakdown (no cross-game aggregation).
    Useful right after creating results for a single match.

    Returns a list of dicts for that game with:
      player, player_id, points, rank, league_points, wins
    Sorted by (-league_points, -points, player)
    """
    lst = list(rows)
    table = _dense_rank_and_share(lst, place_points, win_mode)

    table.sort(key=lambda r: (-r["league_points"], -r["points"], r["player"]))
    if not return_decimals:
        for r in table:
            r["points"] = float(r["points"])
            r["league_points"] = float(r["league_points"])
            r["wins"] = float(r["wins"])
    return table


# ---------- internals ----------

def _dense_rank_and_share(
    lst: List[Row],
    place_points: Dict[int, Decimal],
    win_mode: WinMode,
) -> List[Dict]:
    """
    Given rows for a single selected_game, return per-player dicts:
      player, player_id, points (Decimal), rank (int), league_points (Decimal), wins (Decimal)
    """
    # Sort by position asc (1st place first)
    lst = sorted(lst, key=lambda x: x.position if x.position is not None else 999)

    out: List[Dict] = []
    i = 0
    place = 1
    n = len(lst)

    while i < n:
        # Build tie block [i:j] of same position
        j = i + 1
        p0 = lst[i].position
        while j < n and lst[j].position == p0:
            j += 1
        block = lst[i:j]
        block_size = len(block)

        # Sum league points for occupied places, then share evenly
        occupied = range(place, place + block_size)
        total_for_places = sum(place_points.get(p, Decimal("0")) for p in occupied)
        share = (total_for_places / block_size) if block_size else Decimal("0")

        # Wins assignment
        is_top_block = (place == 1)
        if is_top_block:
            if win_mode == "count_top_block":
                win_shares = [Decimal("1")] * block_size
            elif win_mode == "fractional":
                frac = Decimal("1") / block_size
                win_shares = [frac] * block_size
            elif win_mode == "single":
                win_shares = [Decimal("1")] + [Decimal("0")] * (block_size - 1)
            else:
                raise ValueError("win_mode must be 'count_top_block', 'fractional', or 'single'.")
        else:
            win_shares = [Decimal("0")] * block_size

        # Emit rows
        for k, r in enumerate(block):
            out.append({
                "player": r.player_name,
                "player_id": r.player_id,
                "points": Decimal(r.points) if r.points is not None else Decimal("0"),
                "position": r.position,
                "rank": place,                # dense rank
                "league_points": share,       # shared by the block
                "wins": win_shares[k],
            })

        place += block_size
        i = j

    return out
