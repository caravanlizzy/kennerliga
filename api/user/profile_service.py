import logging

from league.models import League, LeagueResult
from league.service import LeagueService
from season.models import Season
from user.models import PlayerProfile


class ProfileService:

    @staticmethod
    def get_last_participation(player_profile):
        return Season.objects.filter(participants=player_profile).order_by('-year', '-month').first()

    @staticmethod
    def find_player_profile_league(player_profile, season):
        try:
            # Get the league where this player is a member for the given season
            return season.get_leagues().get(members=player_profile)
        except League.DoesNotExist:
            print('Profile did not participate in this season')
            return None  # If no league is found, return None or handle accordingly

    def get_previous_season_result(self, player_profile):
        previous_season = Season.get_previous_season()
        last_particpation = PlayerProfile.get_last_participation()
        if previous_season != last_particpation:
            # has not participated previous season therefore no result
            return None
        previous_league = self.find_player_profile_league(previous_season)
        previous_position = LeagueService.get_league_position(player_profile, previous_league)
        return previous_league, previous_position

    @staticmethod
    def is_last(player_profile: PlayerProfile, league: League):
        """
        Checks if the player is in the last position within the league.
        """
        try:
            league_result = LeagueResult.objects.get(league=league, profile=player_profile)
            return league_result.position == league.members.count()
        except LeagueResult.DoesNotExist:
            logging.warning(f'No league result found for {player_profile} in league {league}.')
            return False
