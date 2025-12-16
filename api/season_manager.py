from season.queries import get_registered_participants, get_open_season
from season.services import SeasonService
from season.services import RankingService


class SeasonManager:
    def start_new_season(self):
        open = get_open_season()
        season_service = SeasonService(open)
        participants = get_registered_participants()
        ranking = RankingService(open)
        ranked = ranking.rank_participants(participants)

        # create leagues before closing season
        season_service.create_leagues(ranked)
        return season_service.open_new()
