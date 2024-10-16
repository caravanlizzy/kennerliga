from league.models import League
from league.service import LeagueService
from season.models import Season
from user.models import PlayerProfile


class ProfileService:

    def get_last_participation(self):
        return Season.objects.filter(participants=self).order_by('-year', '-month').first()

    def find_player_profile_league(self, season):
        try:
            # Get the league where this player is a member for the given season
            return season.get_leagues().get(members=self)
        except League.DoesNotExist:
            print('Profile did not participate in this season')
            return None  # If no league is found, return None or handle accordingly

    def get_previous_season_result(self):
        previous_season = Season.get_previous_season()
        last_particpation = PlayerProfile.get_last_participation()
        if previous_season != last_particpation:
            # has not participated previous season therefore no result
            return None
        previous_league = self.find_player_profile_league(previous_season)
        previous_position = LeagueService.get_league_position(self, previous_league)
        return previous_league, previous_position
