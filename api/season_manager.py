import logging
from django.db import transaction
from season.models import Season
from season.queries import (
    get_registered_participants,
    get_open_season,
    get_running_season,
)
from season.services import (
    close_season,
    rank_participants,
    create_leagues,
    start_open_season,
    create_next_season,
    open_registration,
)
from announcement.services import delete_registration_announcements


def open_next_season(target_season=None):
    """
    Orchestrates opening the next season for registration.
    If target_season is not provided, finds the earliest NEXT season.
    If no NEXT season exists, does nothing.
    """
    if target_season is None:
        target_season = (
            Season.objects.filter(status=Season.SeasonStatus.NEXT)
            .order_by("year", "month")
            .first()
        )

    if not target_season:
        logging.info("No next season found to open for registration. Skipping.")
        return None

    return open_registration(target_season)


def start_new_season(new_season=None):
    """
    Orchestrates the transition to a new season.
    This includes closing the currently running season, ranking participants for the new season,
    creating leagues, and setting up the subsequent next season.
    """
    running_season = get_running_season()
    if new_season is None:
        new_season = get_open_season()

    if not new_season:
        logging.info("No open season found to start. Skipping.")
        return

    with transaction.atomic():
        delete_registration_announcements()
        close_season(running_season)

        participants = list(get_registered_participants(new_season))
        ranked = rank_participants(new_season, participants)

        create_leagues(new_season, ranked)
        start_open_season(new_season)
        create_next_season(new_season)
