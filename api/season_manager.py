import logging
from django.db import transaction
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
)
from announcement.services import delete_registration_announcements


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
