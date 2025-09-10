from season.queries import get_running_season, get_registered_participants
from season.services import SeasonService
from season.services import RankingService


class SeasonManager:
    def start_new_season(self):
        current = get_running_season()
        season_service = SeasonService(current)
        participants = get_registered_participants()

        ranking = RankingService(current)
        ranked = ranking.rank_participants(participants)

        # create leagues before closing season
        season_service.create_leagues(ranked)
        season_service.close_running()
        return season_service.open_new()
