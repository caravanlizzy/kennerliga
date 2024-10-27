import logging
from typing import List

from django.db.models import QuerySet

from season.models import Season
from user.models import PlayerProfile


def get_running_season() -> Season:
    """
    Retrieves the currently running season, if any.
    """
    return Season.objects.filter(status=Season.SeasonStatus.RUNNING).first()

def get_season_by_league(league):
    return league.season


def get_open_season() -> Season:
    """
    Retrieves the season with an open registration, if any.
    """
    return Season.objects.filter(status=Season.SeasonStatus.OPEN).first()


def get_previous_season() -> Season:
    """
    Retrieves the most recently completed season.
    """
    return Season.objects.filter(status=Season.SeasonStatus.DONE).last()


def get_participants(season_name: str) -> List[PlayerProfile]:
    """
    Retrieves all participants of a season by the year (name).
    Assumes that season_name corresponds to the year.
    """
    try:
        season = Season.objects.get(year=season_name)
        return season.participants.all()
    except Season.DoesNotExist:
        logging.warning(f"No season found with year: {season_name}")
        return []


def get_leagues(season: Season) -> QuerySet:
    """
    Retrieves all leagues associated with a given season.
    """
    return season.league_set.all()


def get_registered_participant_count() -> int:
    """
    Returns the number of participants in the current open season.
    If no season is open, returns 0.
    """
    season = get_open_season()
    if season:
        return season.participants.count()
    else:
        logging.info("No open season found.")
        return 0


def get_registered_participants() -> List[PlayerProfile]:
    """
    Returns all participants registered in the current open season.
    If no season is open, returns an empty list.
    """
    season = get_open_season()
    if season:
        return season.participants.all()
    else:
        logging.info("No open season found.")
        return []
