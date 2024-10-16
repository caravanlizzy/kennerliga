from league.models import LeagueResult
from user.models import PlayerProfile
from league.models import League
import logging


class LeagueService:

    @staticmethod
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
