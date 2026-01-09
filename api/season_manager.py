from season.queries import get_registered_participants, get_open_season, get_running_season
from season.services import close_running, rank_participants, create_leagues, open_new, create_next


class SeasonManager:
    def start_new_season(self):
        running_season = get_running_season()
        close_running(running_season)

        open_season = get_open_season()
        participants = get_registered_participants()
        ranked = rank_participants(open_season, participants)

        # create leagues before closing season
        create_leagues(open_season, ranked)
        open_new()
        create_next(open_season)
