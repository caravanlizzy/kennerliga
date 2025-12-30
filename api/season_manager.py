from season.queries import get_registered_participants, get_open_season
from season.services import SeasonService
from season.services import RankingService


class SeasonManager:
    def start_new_season(self):
        running_season = SeasonService()
        running_season.close_running()

        open_season = get_open_season()
        season_service = SeasonService(open_season)
        participants = get_registered_participants()
        ranking = RankingService(open_season)
        ranked = ranking.rank_participants(participants)

        # create leagues before closing season
        season_service.create_leagues(ranked)
        season_service.open_new()
        season_service.create_next()
