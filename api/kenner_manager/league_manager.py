from kenner_manager.season_manager import SeasonManager
from league.models import League
from season.models import Season


class LeagueManager:
    @staticmethod
    def get_league_players_counts(participants_amount: int):
        # Calculate the base number of leagues and the number of leftover players
        league_amount, rest_players = divmod(participants_amount, 4)

        # Initialize the list with 4 players per league
        players_per_league = [4] * league_amount

        # Distribute the leftover players
        if rest_players == 1:
            players_per_league.append(2)  # Create a new league with 2 players
            if league_amount > 0:
                players_per_league[-2] = 3  # Adjust the last full league to have 3 players
        elif rest_players == 2:
            players_per_league.append(2)  # Create a new league with 2 players
        elif rest_players == 3:
            players_per_league.append(3)  # Create a new league with 3 players
        return league_amount, players_per_league

    @staticmethod
    def create_league(season: Season, level: int):
        new_league = League(season=season, level=level)
        new_league.save()
        return new_league

    def create_leagues(self):
        league_amount, players_per_league = self.get_league_players_counts(participants_amount)
        season = SeasonManager.get_open_season()

        if not season:
            print("No open season found.")
            return

        for level in range(1, league_amount + 1):
            league = self.create_league(season, level)
            print(f"Created league at level {level} for season {season}")
            league_amount, players_per_league = self.get_league_players_counts()
            season = SeasonManager.get_open_season()
