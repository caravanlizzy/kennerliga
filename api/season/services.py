import logging
from league.models import League, LeagueStanding
from league.services import set_league_active_player
from season.models import Season, SeasonParticipant
from random import shuffle
from typing import List, Optional
from season.queries import get_previous_season
from user.models import PlayerProfile


def close_season(season: Season):
    if not season:
        logging.warning("No running season to close")
        return
    season.status = Season.SeasonStatus.DONE
    season.save()


def start_open_season(season: Season):
    if not season:
        logging.warning("No open season found")
        return
    if not season.status == Season.SeasonStatus.OPEN:
        logging.warning("Season is not open")
        return
    season.status = Season.SeasonStatus.RUNNING
    season.save()
    return season


def create_next_season(current_season: Season) -> Season:
    if not current_season:
        raise ValueError("No running season found")
    new_month, new_year = _next_month_year(current_season.month, current_season.year)
    new = Season(year=new_year, month=new_month, status=Season.SeasonStatus.NEXT)
    new.save()
    return new


def open_registration(season: Season):
    if not season:
        raise ValueError("No current season")
    season.status = Season.SeasonStatus.OPEN
    season.save()


def create_leagues(season: Season, participants: List) -> List[League]:
    players_per_league = _players_per_league(len(participants))
    leagues = [
        League.objects.create(season=season, level=i + 1)
        for i in range(len(players_per_league))
    ]
    counter = 0

    for league, size in zip(leagues, players_per_league):
        first_participant = None
        for i in range(size):
            participant = participants[counter]
            league.members.add(participant)
            if i == 0:
                first_participant = participant
            counter += 1

        if first_participant is not None:
            set_league_active_player(league, first_participant)

    return leagues


def _next_month_year(month: int, year: int):
    return (1, year + 1) if month == 12 else (month + 1, year)


def _players_per_league(count: int) -> List[int]:
    league_count, rest = divmod(count, 4)
    players = [4] * league_count
    if rest == 1:
        if league_count > 0:
            players[-1] = 3
        players.append(2)
    elif rest == 2:
        players.append(2)
    elif rest == 3:
        players.append(3)
    return players


def rank_participants(
    season: Season, participants: List[SeasonParticipant]
) -> List[SeasonParticipant]:
    """
    This function should order the participants and give them a rank. all participants that have participated in the previous season get rank according how they performed. winner of L1 gets rank1, second in l1 gets #2 etc. first 4 ranks go to L1, then rank 5 is winner of L2 etc. after all participants of the previous seasons have been ranked, the remaining participants get their rank randomly (but increase by one for each nexct participant. the so the last players rank is the amount of players this season
    """
    profiles = [p.profile for p in participants]
    prev_participants_profiles = get_previous_participants_list(profiles)
    new_participants_profiles = [
        p for p in profiles if p not in prev_participants_profiles
    ]

    new_league_sizes = _players_per_league(len(profiles))
    ordered_prev_profiles = order_previous(
        prev_participants_profiles, new_league_sizes
    )

    shuffle(new_participants_profiles)

    final_ordered_profiles = ordered_prev_profiles + new_participants_profiles

    # Map back to SeasonParticipant and set rank
    profile_to_participant = {p.profile_id: p for p in participants}
    ranked_participants = []
    for i, profile in enumerate(final_ordered_profiles, start=1):
        participant = profile_to_participant[profile.id]
        participant.rank = i
        participant.save()
        ranked_participants.append(participant)

    return ranked_participants


def get_previous_participants_list(participants) -> List:
    """
    Filters a given list of participants to obtain those who participated in the
    previous season.

    The function retrieves the participants of the previous season and compares
    them with the provided list of participants. It returns only the participants
    who were also part of the previous season. If there is no previous season, an
    empty list is returned.

    Args:
        participants: List of current participants to be filtered.

    Returns:
        List containing only participants who were part of the previous season.
    """
    prev_season = get_previous_season()
    if not prev_season:
        return []
    prev_participants_profiles = set(
        prev_season.participants.values_list("profile_id", flat=True)
    )
    return [p for p in participants if p.id in prev_participants_profiles]


def get_previous_result(profile: PlayerProfile) -> Optional[dict]:
    prev_season = get_previous_season()
    last_season = (
        Season.objects.filter(
            participants__profile=profile, status=Season.SeasonStatus.DONE
        )
        .order_by("-year", "-month")
        .first()
    )
    if not prev_season or prev_season != last_season:
        return None

    return _result_for_season(profile, prev_season)


def _result_for_season(profile: PlayerProfile, season: Season) -> Optional[dict]:
    try:
        league = League.objects.get(season=season, members__profile=profile)
    except League.DoesNotExist:
        return None

    # Get standings for this league ordered by performance (descending)
    standings = list(
        LeagueStanding.objects.filter(league=league).order_by(
            "-league_points", "-wins", "player_profile__profile_name"
        )
    )

    # Find this player's standing and rank
    player_standing = next(
        (s for s in standings if s.player_profile_id == profile.id), None
    )
    if not player_standing:
        return None

    rank = standings.index(player_standing) + 1

    return {
        "league": league.level,
        "position": rank,
        "is_last": (rank == len(standings) and len(standings) > 1),
    }


def get_projection_result(profile: PlayerProfile) -> Optional[dict]:
    """Return a 'previous result' for projection purposes.

    Used by the sign-up preview to project the next season's leagues even
    when the previous season has not been finalized yet. Prefers the
    currently RUNNING season's live standings; falls back to the most
    recent DONE season otherwise. Returns ``None`` if the player has no
    relevant standing in either.
    """
    from season.queries import get_running_season

    running = get_running_season()
    if running is not None:
        result = _result_for_season(profile, running)
        if result is not None:
            return result
    # Fall back to the finalized previous season.
    return get_previous_result(profile)


def order_previous(
    participants: List[PlayerProfile],
    new_league_sizes: Optional[List[int]] = None,
) -> List[PlayerProfile]:
    data = []
    for p in participants:
        info = get_previous_result(p)
        if info and info["position"] is not None:
            data.append(
                {
                    "profile": p,
                    "league": info["league"],
                    "position": info["position"],
                    "is_last": info["is_last"],
                }
            )

    promoted = apply_promotion(data, new_league_sizes)
    return [row["profile"] for row in promoted]


def _target_league(row: dict, num_new_leagues: Optional[int] = None) -> int:
    """Determine the new league level a previous-season player aims for.

    The previous league index is first clamped to the new structure size so
    that — when the new season has fewer leagues than the previous one
    (e.g. due to non-registration of whole leagues) — the pyramid is
    compressed proportionally. Promotion/relegation offsets are then
    applied on top of the clamped value.

    - Winner (position 1) of a non-top league is guaranteed a promotion.
    - Last position in a league forces a relegation.
    - Otherwise, stay in (the clamped) league.
    """
    league = row["league"]
    if num_new_leagues is None or num_new_leagues <= 0:
        clamped = league
        cap = league + 1
    else:
        clamped = min(league, num_new_leagues)
        cap = num_new_leagues
    if row["position"] == 1 and league > 1:
        return max(1, clamped - 1)
    if row["is_last"]:
        return min(cap, clamped + 1)
    return clamped


def _sort_key(row: dict, num_new_leagues: Optional[int] = None):
    return (_target_league(row, num_new_leagues), row["league"], row["position"])


def apply_promotion(
    participants: List[dict],
    new_league_sizes: Optional[List[int]] = None,
) -> List[dict]:
    """Order previous-season registered players for the next season,
    enforcing two rules:

    1. A player who won their league (position 1, league > 1) is guaranteed
       to be promoted: they must end up in a strictly higher league than
       before. If capacity in the target league is full, the lowest-ranked
       non-guaranteed player of that league is relegated to make room
       (e.g. the 3rd of the higher league).
    2. A player who finished last in their league is guaranteed to be
       relegated: they must end up in a strictly lower league than before.
       If that means another player has to be promoted from below to fill
       the gap, that promotion happens.
    """
    if not participants:
        return []

    num_new = len(new_league_sizes) if new_league_sizes else 0

    def _key(row: dict):
        return _sort_key(row, num_new if num_new > 0 else None)

    # Sort by (target_league, prev_league, prev_position) as the baseline.
    ordered = sorted(participants, key=_key)

    # Without explicit league sizes, fall back to the baseline order.
    if not new_league_sizes:
        return ordered

    # Assign rows to new leagues by capacity. Only the prefix of new
    # leagues that this group of previous players occupies is relevant.
    league_assignment: List[List[dict]] = []
    idx = 0
    for size in new_league_sizes:
        if idx >= len(ordered):
            break
        chunk = ordered[idx : idx + size]
        league_assignment.append(chunk)
        idx += size
        if idx >= len(ordered):
            break

    def _is_guaranteed_promotion(row: dict) -> bool:
        return row["position"] == 1 and row["league"] > 1

    def _is_guaranteed_relegation(row: dict) -> bool:
        return row["is_last"]

    # Iteratively fix violations until stable. Each pass either resolves a
    # violation by swapping a guaranteed-move player with a non-guaranteed
    # one in the adjacent league, or stops.
    changed = True
    safety = 0
    while changed and safety < 100:
        changed = False
        safety += 1

        # Rule 1: every guaranteed-promotion player must be in a new league
        # strictly above their (clamped) previous league.
        for new_level_idx, league in enumerate(league_assignment):
            new_level = new_level_idx + 1
            for row in list(league):
                prev_clamped = (
                    min(row["league"], num_new) if num_new > 0 else row["league"]
                )
                if (
                    _is_guaranteed_promotion(row)
                    and new_level >= prev_clamped
                    and new_level_idx > 0
                ):
                    # Find a non-guaranteed swap candidate in the league above
                    # (lowest-ranked one) to relegate.
                    above = league_assignment[new_level_idx - 1]
                    candidates = [
                        r
                        for r in above
                        if not _is_guaranteed_promotion(r)
                        and not _is_guaranteed_relegation(r)
                    ]
                    if not candidates:
                        continue
                    victim = max(candidates, key=_key)
                    above.remove(victim)
                    above.append(row)
                    league.remove(row)
                    league.append(victim)
                    above.sort(key=_key)
                    league.sort(key=_key)
                    changed = True
                    break
            if changed:
                break
        if changed:
            continue

        # Rule 2: every guaranteed-relegation player must be in a new league
        # strictly below their (clamped) previous league.
        for new_level_idx, league in enumerate(league_assignment):
            new_level = new_level_idx + 1
            for row in list(league):
                prev_clamped = (
                    min(row["league"], num_new) if num_new > 0 else row["league"]
                )
                if (
                    _is_guaranteed_relegation(row)
                    and new_level <= prev_clamped
                    and new_level_idx + 1 < len(league_assignment)
                ):
                    below = league_assignment[new_level_idx + 1]
                    candidates = [
                        r
                        for r in below
                        if not _is_guaranteed_promotion(r)
                        and not _is_guaranteed_relegation(r)
                    ]
                    if not candidates:
                        continue
                    victim = min(candidates, key=_key)
                    below.remove(victim)
                    below.append(row)
                    league.remove(row)
                    league.append(victim)
                    below.sort(key=_key)
                    league.sort(key=_key)
                    changed = True
                    break
            if changed:
                break

    result: List[dict] = []
    for league in league_assignment:
        result.extend(league)
    return result
