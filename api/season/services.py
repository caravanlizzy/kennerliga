import logging
from league.models import League, LeagueStanding
from season.models import Season, SeasonParticipant
from season.queries import get_running_season, get_open_season
from random import shuffle
from typing import List, Dict, Optional, Any
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
    new = Season(year=new_year, month=new_month, status=Season.SeasonStatus.OPEN)
    new.save()
    return new

def open_registration(season: Season):
    if not season:
        raise ValueError("No current season")
    season.status = Season.SeasonStatus.OPEN
    season.save()

def create_leagues(season: Season, participants: List) -> List[League]:
    players_per_league = _players_per_league(len(participants))
    leagues = [League.objects.create(season=season, level=i + 1)
               for i in range(len(players_per_league))]
    counter = 0
    for league, size in zip(leagues, players_per_league):
        for _ in range(size):
            league.members.add(participants[counter])
            counter += 1
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


def rank_participants(season: Season, participants: List[SeasonParticipant]) -> List[SeasonParticipant]:
    """
    This function should order the participants and give them a rank. all participants that have participated in the previous season get rank according how they performed. winner of L1 gets rank1, second in l1 gets #2 etc. first 4 ranks go to L1, then rank 5 is winner of L2 etc. after all participants of the previous seasons have been ranked, the remaining participants get their rank randomly (but increase by one for each nexct participant. the so the last players rank is the amount of players this season
    """
    profiles = [p.profile for p in participants]
    prev_participants_profiles = get_previous_participants_list(profiles)
    new_participants_profiles = [p for p in profiles if p not in prev_participants_profiles]

    ordered_prev_profiles = order_previous(prev_participants_profiles)

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
    prev_participants_profiles = set(prev_season.participants.values_list('profile_id', flat=True))
    return [p for p in participants if p.id in prev_participants_profiles]

def get_previous_result(profile: PlayerProfile) -> Optional[dict]:
    prev_season = get_previous_season()
    last_season = Season.objects.filter(participants__profile=profile, status=Season.SeasonStatus.DONE).order_by("-year", "-month").first()
    if not prev_season or prev_season != last_season:
        return None

    try:
        league = League.objects.get(season=prev_season, members__profile=profile)
    except League.DoesNotExist:
        return None

    # Get standings for this league ordered by performance (descending)
    standings = list(
        LeagueStanding.objects.filter(league=league)
        .order_by("-league_points", "-wins", "player_profile__profile_name")
    )
    
    # Find this player's standing and rank
    player_standing = next((s for s in standings if s.player_profile_id == profile.id), None)
    if not player_standing:
        return None
        
    rank = standings.index(player_standing) + 1
    
    return {
        "league": league.level,
        "position": rank,
        "is_last": (rank == len(standings) and len(standings) > 1),
    }

def order_previous(participants: List[PlayerProfile]) -> List[PlayerProfile]:
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

    sorted_list = sorted(data, key=lambda x: (x["league"], x["position"]))
    promoted = apply_promotion(sorted_list)
    return [row["profile"] for row in promoted]

def apply_promotion(participants: List[dict]) -> List[dict]:
    # Apply simple promotion/relegation rule
    participants_copy = participants.copy()
    for i, current in enumerate(participants_copy[1:], start=1):
        prev = participants_copy[i - 1]
        if prev["is_last"] and current["league"] - 1 == prev["league"] and current["position"] == 1:
            participants_copy[i], participants_copy[i - 1] = prev, current
    return participants_copy
