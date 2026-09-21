from collections import defaultdict

from django.db.models import Count
from typing import List, Dict, Any
from league.models import League, LeagueStanding
from game.models import SelectedGame, BanDecision
from api.constants import get_ban_amount_for_success, get_game_picks_per_player


def get_members_ordered(league: League):
    """
    Returns the league members ordered by their season rank.
    """
    return league.members.all().select_related("profile").order_by("rank")


def all_players_have_picked(league: League) -> bool:
    """
    Checks if all players in the league have selected the expected number of games.
    """
    members = league.members.all()
    member_count = members.count()
    expected_count = get_game_picks_per_player(member_count)

    pick_counts = (
        SelectedGame.objects.filter(league=league)
        .values("profile")
        .annotate(count=Count("id"))
    )

    pick_counts_map = {item["profile"]: item["count"] for item in pick_counts}

    for participant in members:
        if pick_counts_map.get(participant.profile_id, 0) < expected_count:
            return False
    return True


def all_players_have_banned(league: League) -> bool:
    """
    Checks if all players in the league have submitted at least one ban decision.
    """
    members = league.members.all()
    expected_ban_count = 1

    ban_counts = (
        BanDecision.objects.filter(league=league)
        .values("player_banning")
        .annotate(count=Count("id"))
    )

    ban_counts_map = {item["player_banning"]: item["count"] for item in ban_counts}

    for participant in members:
        if ban_counts_map.get(participant.profile_id, 0) < expected_ban_count:
            return False
    return True


def get_players_to_repick(league: League) -> List:
    """
    Identifies league members who need to pick another game because one of their initial picks was banned.
    """
    members = list(league.members.all().select_related("profile"))
    required_bans = get_ban_amount_for_success(len(members))

    # Get all banned game IDs for this league
    banned_game_ids = set(
        BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=required_bans)
        .values_list("selected_game_id", flat=True)
    )
    if not banned_game_ids:
        return []

    # Load every pick of the league once and bucket it per profile, instead
    # of running two queries per member.
    picks_by_profile: Dict[int, List[int]] = defaultdict(list)
    for sg_id, profile_id in SelectedGame.objects.filter(league=league).order_by(
        "id"
    ).values_list("id", "profile_id"):
        picks_by_profile[profile_id].append(sg_id)

    # Only a player's first two picks can trigger a repick.
    return [
        member
        for member in members
        if any(
            sg_id in banned_game_ids
            for sg_id in picks_by_profile.get(member.profile_id, [])[:2]
        )
    ]


def all_repickers_have_repicked(league: League) -> bool:
    """
    Checks if all players identified for repicking have completed their additional selections.
    """
    repickers = get_players_to_repick(league)
    if not repickers:
        return True

    expected_count = get_game_picks_per_player(league.members.count()) + 1

    # For 2-player leagues, players should have 3 games if they had to repick;
    # for other leagues, more than 1. One grouped query covers every repicker.
    pick_counts = {
        row["profile"]: row["c"]
        for row in SelectedGame.objects.filter(
            league=league, profile__in=[p.profile_id for p in repickers]
        )
        .values("profile")
        .annotate(c=Count("id"))
    }

    return all(
        pick_counts.get(player.profile_id, 0) >= expected_count
        for player in repickers
    )


def is_two_player_league(league: League) -> bool:
    """
    Returns True if the league has exactly two members.
    """
    return league.members.count() == 2


def both_players_exactly_one_pick(league: League) -> bool:
    """
    Returns True if exactly two games have been selected in total for the league.
    Used in two-player league logic.
    """
    return SelectedGame.objects.filter(league=league).count() == 2


def is_league_finished(league: League) -> bool:
    """
    Checks if all non-banned game selections in the league have recorded results.
    """
    return are_leagues_finished([league]).get(league.id, False)


def are_leagues_finished(leagues: List[League]) -> Dict[int, bool]:
    """
    Bulk variant of :func:`is_league_finished`.

    Answers "is this league finished?" for many leagues using a constant
    number of queries (four) instead of the ``O(leagues x games)`` fan-out
    you get from calling ``league.is_finished`` in a loop. A league counts
    as finished when every non-banned SelectedGame in it has a Result for
    each of its members.
    """
    from result.models import Result

    league_ids = [lg.id for lg in leagues]
    if not league_ids:
        return {}

    # 1. Member count per league (one query over the M2M through table).
    member_counts: Dict[int, int] = {lid: 0 for lid in league_ids}
    for row in (
        League.members.through.objects.filter(league_id__in=league_ids)
        .values("league_id")
        .annotate(c=Count("id"))
    ):
        member_counts[row["league_id"]] = row["c"]

    # 2. Successfully banned games per league. The ban threshold depends on
    #    the league's member count, so count bans per game and compare in
    #    Python rather than issuing one filtered query per league.
    ban_counts: Dict[int, Dict[int, int]] = defaultdict(dict)
    for row in (
        BanDecision.objects.filter(
            league_id__in=league_ids, selected_game__isnull=False
        )
        .values("league_id", "selected_game_id")
        .annotate(c=Count("id"))
    ):
        ban_counts[row["league_id"]][row["selected_game_id"]] = row["c"]

    # 3. All SelectedGames of these leagues.
    games_by_league: Dict[int, List[int]] = defaultdict(list)
    for sg_id, lid in SelectedGame.objects.filter(
        league_id__in=league_ids
    ).values_list("id", "league_id"):
        games_by_league[lid].append(sg_id)

    # 4. Result count per SelectedGame.
    result_counts: Dict[int, int] = {}
    for row in (
        Result.objects.filter(league_id__in=league_ids)
        .values("selected_game_id")
        .annotate(c=Count("id"))
    ):
        result_counts[row["selected_game_id"]] = row["c"]

    finished: Dict[int, bool] = {}
    for lid in league_ids:
        member_count = member_counts.get(lid, 0)
        if member_count == 0:
            finished[lid] = False
            continue

        expected_games_count = member_count * get_game_picks_per_player(member_count)
        required_bans = get_ban_amount_for_success(member_count)

        league_ban_counts = ban_counts.get(lid, {})
        active_game_ids = [
            sg_id
            for sg_id in games_by_league.get(lid, [])
            if league_ban_counts.get(sg_id, 0) < required_bans
        ]

        if len(active_game_ids) < expected_games_count:
            # Not all games have been picked/repicked yet
            finished[lid] = False
            continue

        finished[lid] = all(
            result_counts.get(sg_id, 0) >= member_count for sg_id in active_game_ids
        )

    return finished


def detect_unresolved_tie_groups(league: League) -> List[Dict[str, Any]]:
    """
    Detect unresolved tie groups for a given league based on LeagueStanding.

    Returns a list of dicts:
    {
      "group_key": str,
      "members": [player_profile_id, ...],
      "size": int,
      "league_points": Decimal,   # shared among group
      "wins": Decimal             # shared among group
    }

    Notes:
    - This relies on `services.standings_snapshot.rebuild_league_snapshot` having
      been run, which populates `unresolved_tie_group` whenever players share
      the same (league_points, wins) and no manual tie priority is present.
    - Groups with size == 1 are not returned.
    """
    qs = LeagueStanding.objects.filter(
        league=league, unresolved_tie_group__isnull=False
    ).only("player_profile_id", "league_points", "wins", "unresolved_tie_group")

    buckets: Dict[str, Dict[str, Any]] = {}
    for ls in qs:
        key = ls.unresolved_tie_group
        if key not in buckets:
            buckets[key] = {
                "group_key": key,
                "members": [],
                "size": 0,
                "league_points": ls.league_points,
                "wins": ls.wins,
            }
        buckets[key]["members"].append(ls.player_profile_id)
        buckets[key]["size"] += 1

    # Filter out singleton groups just in case
    groups = [g for g in buckets.values() if g["size"] > 1]

    # Stable ordering: highest points/wins first, then by key
    groups.sort(key=lambda g: (-g["league_points"], -g["wins"], g["group_key"]))
    return groups


def has_unresolved_ties(league: League) -> bool:
    """Quick boolean check for any unresolved tie groups in a league."""
    return LeagueStanding.objects.filter(
        league=league, unresolved_tie_group__isnull=False
    ).exists()
