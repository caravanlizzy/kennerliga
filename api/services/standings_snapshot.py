from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.db import transaction
from result.models import Result
from services.scoring import Row, compute_game_breakdown, compute_league_table
from league.models import LeagueStanding, GameStanding, League
from game.models import SelectedGame, ResultConfig


@transaction.atomic
def rebuild_game_snapshot(selected_game, win_mode: str = "count_top_block") -> None:
    """
    Rebuild per-game standings for a single SelectedGame.

    - If ResultConfig.has_points is True:
        * Uses Result.points as the score (higher is better).
    - If has_points is False:
        * Uses -position as the score (lower position => higher score).
    - Stores the score in GameStanding.points (Decimal).
    - Computes dense ranks.
    - For win_mode == "count_top_block":
        * Rank 1 players share win_share = 1 / number_of_first_place_players.
        * league_points equals win_share (adjust if you have a different rule).
    """
    # Load all results for this selected game
    results = (
        Result.objects
        .filter(selected_game=selected_game)
        .select_related("player_profile", "league")
    )

    # If there are no results, clear any old standings and exit
    if not results.exists():
        GameStanding.objects.filter(selected_game=selected_game).delete()
        return

    league = selected_game.league

    try:
        result_config = ResultConfig.objects.get(game=selected_game.game)
    except ResultConfig.DoesNotExist:
        # No config → clear standings and bail
        GameStanding.objects.filter(selected_game=selected_game).delete()
        return

    use_points = result_config.has_points

    # ------------------------------------------------------------------
    # Build rows with a numeric score for each player
    # ------------------------------------------------------------------
    rows: list[dict] = []

    for r in results:
        if use_points:
            raw = r.points if r.points is not None else 0
        else:
            # Position-based: smaller position is better
            if r.position is None:
                # if this happens something went wrong in validation; treat as worst
                raw = 999999
            else:
                # Store negative position so "higher is better"
                raw = -int(r.position)

        try:
            score = Decimal(raw)
        except (InvalidOperation, TypeError, ValueError):
            score = Decimal("0")

        rows.append(
            {
                "profile": r.player_profile,
                "score": score,
            }
        )

    # Sort descending by score (because higher = better in both modes)
    rows.sort(key=lambda x: x["score"], reverse=True)

    # ------------------------------------------------------------------
    # Dense rank assignment
    # ------------------------------------------------------------------
    dense_rank = 0
    last_score: Decimal | None = None

    for index, row in enumerate(rows):
        if last_score is None or row["score"] != last_score:
            dense_rank = index + 1
        row["rank"] = dense_rank
        last_score = row["score"]

    # ------------------------------------------------------------------
    # League points / win share
    # ------------------------------------------------------------------
    rank_groups: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        rank_groups[row["rank"]].append(row)

    # Default values
    for row in rows:
        row["win_share"] = Decimal("0.00")
        row["league_points"] = Decimal("0.00")

    if win_mode == "count_top_block":
        # Only rank 1 gets win share; shared among all first-place players
        first_group = rank_groups.get(1, [])
        if first_group:
            share = Decimal("1.00") / Decimal(len(first_group))
            # Round to 2 decimal places to match GameStanding fields
            share = share.quantize(Decimal("0.01"))

            for row in first_group:
                row["win_share"] = share
                row["league_points"] = share

    # ------------------------------------------------------------------
    # Persist standings
    # ------------------------------------------------------------------
    with transaction.atomic():
        GameStanding.objects.filter(selected_game=selected_game).delete()

        objs: list[GameStanding] = []
        for row in rows:
            objs.append(
                GameStanding(
                    league=league,
                    selected_game=selected_game,
                    player_profile=row["profile"],
                    points=row["score"].quantize(Decimal("0.01")),
                    rank=row["rank"],
                    league_points=row["league_points"],
                    win_share=row["win_share"],
                )
            )

        GameStanding.objects.bulk_create(objs)


@transaction.atomic
def rebuild_league_snapshot(league: League, *, win_mode: str = "count_top_block"):
    # compute over all results in league
    qs = (
        Result.objects
        .filter(league=league)
        .select_related("selected_game", "player_profile")
        .only("selected_game_id", "player_profile", "player_profile__profile_name", "points")
    )

    def dec_or_zero(value):
        try:
            # handle None, '', etc.
            return Decimal(value if value is not None else 0)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal(0)

    rows = [
        Row(
            selected_game_id=r.selected_game_id,
            player_id=r.player_profile,                # keep as you had it
            player_name=r.player_profile.profile_name,
            points=dec_or_zero(r.points),              # <-- safe conversion
        )
        for r in qs
    ]

    table = compute_league_table(rows, win_mode=win_mode, return_decimals=True)

    # upsert LeagueStanding (NO raw points)
    existing = {ls.player_profile: ls for ls in LeagueStanding.objects.filter(league=league)}
    to_create, to_update = [], []

    for r in table:
        obj = existing.get(r["player_id"])
        if obj is None:
            to_create.append(LeagueStanding(
                league=league,
                player_profile=r["player_id"],
                wins=r["wins"],
                league_points=r["league_points"],
            ))
        else:
            obj.wins = r["wins"]
            obj.league_points = r["league_points"]
            to_update.append(obj)

    if to_create:
        LeagueStanding.objects.bulk_create(to_create)
    if to_update:
        LeagueStanding.objects.bulk_update(to_update, ["wins", "league_points"])
