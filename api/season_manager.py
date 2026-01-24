from django.db import transaction
from season.queries import get_registered_participants, get_open_season, get_running_season
from season.services import close_season, rank_participants, create_leagues, start_open_season, create_next_season


def start_new_season():
    running_season = get_running_season()
    new_season = get_open_season()

    if not new_season:
        raise ValueError("No open season found to start")

    with transaction.atomic():
        close_season(running_season)

        participants = list(get_registered_participants())
        ranked = rank_participants(new_season, participants)

        create_leagues(new_season, ranked)
        start_open_season(new_season)
        create_next_season(new_season)
