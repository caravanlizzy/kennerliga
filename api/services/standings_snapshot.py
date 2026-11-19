from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.db import transaction
from result.models import Result
from api.constants import get_league_points
from services.scoring import Row, compute_league_table
from league.models import LeagueStanding, GameStanding, League, LeagueTieResolution
from game.models import ResultConfig


@transaction.atomic
def rebuild_game_snapshot(selected_game, win_mode: str = "fractional") -> None:
    """
    Rebuild per-game standings for a single SelectedGame.
    - Uses Result.position for sorting and ranking (pre-calculated with tie-breakers).
    - If ResultConfig.has_points is True:
        * Stores Result.points in GameStanding.points.
    - If has_points is False:
        * Stores -position in GameStanding.points.
    - Computes dense ranks based on position.
    - For win_mode == "fractional":
        * Rank 1 players share win_share = 1 / number_of_first_place_players.
    """
    # Load all results for this selected game
    results = Result.objects.filter(selected_game=selected_game).select_related(
        "player_profile", "league"
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
    # Build rows based on pre-calculated position
    # ------------------------------------------------------------------
    rows: list[dict] = []
    for r in results:
        pos = r.position if r.position is not None else 999
        if use_points:
            score = Decimal(r.points if r.points is not None else 0)
        else:
            # Store negative position so sorting/points remain consistent with "score"
            score = Decimal(-int(pos))

        rows.append(
            {
                "profile": r.player_profile,
                "score": score,
                "position": int(pos),
                "decisive_tie_breaker": r.decisive_tie_breaker,
                "tie_breaker_value": r.tie_breaker_value,
            }
        )

    # Sort by position (ascending, lower is better)
    rows.sort(key=lambda x: x["position"])

    # ------------------------------------------------------------------
    # Dense rank assignment based on position
    # ------------------------------------------------------------------
    dense_rank = 0
    last_pos: int | None = None

    for index, row in enumerate(rows):
        if last_pos is None or row["position"] != last_pos:
            dense_rank = index + 1
        row["rank"] = dense_rank
        last_pos = row["position"]

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

    # First: win_share
    if win_mode == "count_top_block":
        first_group = rank_groups.get(1, [])
        for row in first_group:
            row["win_share"] = Decimal("1.00")
    elif win_mode == "fractional":
        first_group = rank_groups.get(1, [])
        if first_group:
            share = (Decimal("1.00") / Decimal(len(first_group))).quantize(
                Decimal("0.01")
            )
            for row in first_group:
                row["win_share"] = share
    elif win_mode == "single":
        first_group = rank_groups.get(1, [])
        if first_group:
            # exactly one win
            first_group[0]["win_share"] = Decimal("1.00")

    # Then: league points distribution based on player count, with tie handling
    player_count = Result.objects.filter(selected_game=selected_game).count()
    POINTS_TABLE = get_league_points(player_count)

    # We walk rank groups in order and assign places 1..N
    current_place = 1
    for rank in sorted(rank_groups.keys()):
        group = rank_groups[rank]
        group_size = len(group)

        # Points for the places this tied group occupies
        raw_points = []
        for offset in range(group_size):
            place = current_place + offset
            raw_points.append(POINTS_TABLE.get(place, Decimal("0")))

        avg_points = (sum(raw_points, Decimal("0")) / group_size).quantize(
            Decimal("0.01")
        )

        for row in group:
            row["league_points"] = avg_points

        current_place += group_size

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
                    decisive_tie_breaker=row.get("decisive_tie_breaker"),
                    tie_breaker_value=row.get("tie_breaker_value"),
                )
            )

        GameStanding.objects.bulk_create(objs)


@transaction.atomic
def rebuild_league_snapshot(league: League, *, win_mode: str = "fractional"):
    # compute over all results in league
    qs = (
        Result.objects.filter(league=league)
        .select_related("selected_game", "player_profile")
        .only(
            "selected_game_id",
            "player_profile",
            "player_profile__profile_name",
            "points",
            "position",
        )
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
            player_id=r.player_profile.id,
            player_name=r.player_profile.profile_name,
            points=dec_or_zero(r.points),
            position=r.position,  # Add this line
        )
        for r in qs
    ]

    table = compute_league_table(rows, win_mode=win_mode, return_decimals=True)

    sorted_table = sorted(
        table, key=lambda r: (r["league_points"], r["wins"], r["second_places"], r["third_places"]), reverse=True
    )

    # upsert LeagueStanding (NO raw points)
    existing = {
        ls.player_profile_id: ls for ls in LeagueStanding.objects.filter(league=league)
    }

    # Build contiguous groups equal on every automatic tie-break criterion.
    groups: list[tuple[str, list[dict]]] = []
    current_group: list[dict] = []
    current_key: str | None = None

    def make_key(lp, wins, seconds, thirds) -> str:
        # Use quantized strings to ensure stable keys
        lp_s = f"{lp:.2f}" if hasattr(lp, "quantize") else str(lp)
        wins_s = f"{wins:.2f}" if hasattr(wins, "quantize") else str(wins)
        return f"lp:{lp_s}|w:{wins_s}|s:{seconds}|t:{thirds}"

    for row in sorted_table:
        key = make_key(row["league_points"], row["wins"], row["second_places"], row["third_places"])
        if current_key is None:
            current_key = key
            current_group = [row]
        elif key == current_key:
            current_group.append(row)
        else:
            if len(current_group) > 1:
                groups.append((current_key, current_group))
            current_key = key
            current_group = [row]
    if len(current_group) > 1:
        groups.append((current_key, current_group))

    # Map player_id -> group_key
    player_to_group: dict[int, str] = {}
    for gkey, members in groups:
        for m in members:
            player_id = m["player_id"]
            player_to_group[player_id] = gkey

    # Retain manual decisions only when the exact same players remain tied.
    group_members = {key: {row["player_id"] for row in members} for key, members in groups}
    priorities = {}
    for resolution in LeagueTieResolution.objects.filter(league=league).prefetch_related("entries"):
        member_ids = {entry.player_profile_id for entry in resolution.entries.all()}
        new_key = next((key for key, ids in group_members.items() if ids == member_ids), None)
        if new_key and resolution.group_key != new_key:
            if not LeagueTieResolution.objects.filter(league=league, group_key=new_key).exists():
                resolution.group_key = new_key
                resolution.save(update_fields=["group_key"])
        if new_key and resolution.group_key == new_key and resolution.is_resolved:
            entries = sorted(resolution.entries.all(), key=lambda entry: entry.order_index)
            priorities.update({entry.player_profile_id: len(entries) - i for i, entry in enumerate(entries)})

    # ------------------------------------------------------------------
    # upsert LeagueStanding (NO raw points)
    # ------------------------------------------------------------------
    to_create, to_update = [], []

    for r in table:
        player_id = r["player_id"]
        obj = existing.get(player_id)
        group_key = player_to_group.get(player_id)

        # IMPORTANT: Even if a tie is resolved (priority > 0), we still store
        # the group_key if there is a tie in points/wins. This allows the UI
        # to show the "resolved" state (with the reason) instead of nothing.
        # The group_key is used to look up LeagueTieResolution.

        if obj is None:
            to_create.append(
                LeagueStanding(
                    league=league,
                    player_profile_id=r["player_id"],
                    wins=r["wins"],
                    second_places=r["second_places"],
                    third_places=r["third_places"],
                    tie_break_priority=priorities.get(player_id, 0),
                    league_points=r["league_points"],
                    unresolved_tie_group=group_key,
                )
            )
        else:
            obj.wins = r["wins"]
            obj.second_places = r["second_places"]
            obj.third_places = r["third_places"]
            obj.tie_break_priority = priorities.get(player_id, 0)
            obj.league_points = r["league_points"]
            obj.unresolved_tie_group = group_key
            to_update.append(obj)

    if to_create:
        LeagueStanding.objects.bulk_create(to_create)
    if to_update:
        LeagueStanding.objects.bulk_update(
            to_update, ["wins", "second_places", "third_places", "tie_break_priority", "league_points", "unresolved_tie_group"]
        )
