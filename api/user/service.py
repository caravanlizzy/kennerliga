import logging
from typing import Union, Optional, Dict

from league.models import League, LeagueResult
from season.models import Season
from season.service import get_previous_season, get_leagues
from user.models import PlayerProfile, User


def get_last_participation(player_profile: PlayerProfile) -> Season:
    """
    Retrieves the last season in which the player participated.
    """
    return Season.objects.filter(participants=player_profile).order_by('-year', '-month').first()


def find_player_profile_league(player_profile: PlayerProfile, season: Season) -> Union[League, None]:
    """
    Finds the league for a player profile in a given season.
    """
    try:
        # Get the league where this player is a member for the given season
        return get_leagues(season).get(members=player_profile)
    except League.DoesNotExist:
        print('Profile did not participate in this season')
        return None  # If no league is found, return None or handle accordingly


def get_league_position(player_profile: PlayerProfile, league: League):
    """
    Retrieves the league position or points of the given player in the specified league.
    """
    try:
        result = LeagueResult.objects.filter(league=league, profile=player_profile).first()

        if result:
            return result.league_points  # Or whatever defines 'position'
        else:
            logging.info(f'No league result found for player {player_profile} in league {league}')
            return None  # Or a default value like 0 or -1 to indicate no result

    except Exception as e:
        logging.error(f"Error while retrieving league position: {e}")
        return None


def is_last(player_profile: PlayerProfile, league: League) -> bool:
    """
    Checks if the player is in the last position within the league.
    """
    try:
        league_result = LeagueResult.objects.get(league=league, profile=player_profile)
        return league_result.position == league.members.count()
    except LeagueResult.DoesNotExist:
        logging.warning(f'No league result found for {player_profile} in league {league}.')
        return False


def get_previous_season_result(player_profile: PlayerProfile) -> Optional[Dict]:
    """
    Retrieves the previous season's league and position for the player profile.
    Returns None if the player did not participate.
    """
    previous_season = get_previous_season()
    last_participation = get_last_participation(player_profile)

    if previous_season != last_participation:
        # Has not participated in the previous season, therefore no result
        return None

    previous_league = find_player_profile_league(player_profile, previous_season)
    previous_position = get_league_position(player_profile, previous_league) if previous_league else None
    previous_is_last = is_last(player_profile, previous_league)

    return {
        "league": previous_league,
        "position": previous_position,
        "is_last": previous_is_last,
    }


def create_profile_for_user(user):
    profile_name = user.username + '_profile'
    new_profile = PlayerProfile(user=user, profile_name=profile_name)
    new_profile.save()


def create_user(username):
    if User.objects.filter(username=username).exists():
        logging.error(f"User {username} already exists.")
        return
    new_user = User(username=username)
    new_user.save()
    create_profile_for_user(new_user)