import logging
from random import shuffle
from typing import List, Dict

from league.models import League
from season.models import Season
from season.service import get_running_season, get_open_season, get_registered_participants, get_previous_season
from user.models import PlayerProfile
from user.profile_service import get_previous_season_result


class SeasonManager:
    def __init__(self):
        self.current_season = get_running_season()
        self.open_season = get_open_season()

    def refresh_season_data(self):
        """Refresh the current and open season data."""
        self.current_season = get_running_season()
        self.open_season = get_open_season()

    def create_new_season(self):
        """Create the next season based on the current running season."""
        if not self.current_season:
            logging.error("No running season found.")
            return False
        try:
            new_month, new_year = self.get_new_month_year(self.current_season.month, self.current_season.year)
            new_season = Season(year=new_year, month=new_month, status=Season.SeasonStatus.OPEN)
            new_season.save()
            logging.info(f"Next season created: {new_season.year}-{new_season.month}, Status: {new_season.status}")
            self.refresh_season_data()
            return True
        except Exception as e:
            logging.error(f"Failed to create new season: {e}")
            return False

    def create_league(self, level: int):
        """Create a new league at a specific level for the current open season."""
        try:
            new_league = League(season=self.open_season, level=level)
            new_league.save()
            logging.info(f"Created league at level {level} for season {self.open_season}")
            return new_league
        except Exception as e:
            logging.error(f"Failed to create league at level {level}: {e}")
            return None

    def start_season(self):
        """Start the current open season."""
        if self.open_season:
            self.open_season.status = Season.SeasonStatus.RUNNING
            self.open_season.save()
            logging.info(f"Season {self.open_season.year}-{self.open_season.month} started.")
        else:
            logging.warning("No open season found to start.")

    def open_registration(self):
        """Open registration for the current running season."""
        if self.current_season:
            self.current_season.status = Season.SeasonStatus.OPEN
            self.current_season.save()
            logging.info(f"Registration opened for season {self.current_season.year}-{self.current_season.month}.")
        else:
            logging.warning("No running season available for registration.")

    @staticmethod
    def get_players_per_league(participants_amount: int) -> List[int]:
        """
        Calculate how many players should be in each league based on the total number of participants.
        """
        league_amount, rest_players = divmod(participants_amount, 4)
        players_per_league = [4] * league_amount

        if rest_players == 1:
            players_per_league.append(2)
            if league_amount > 0:
                players_per_league[-2] = 3
        elif rest_players == 2:
            players_per_league.append(2)
        elif rest_players == 3:
            players_per_league.append(3)

        return players_per_league

    def create_leagues(self, participants_count: int):
        """
        Create leagues for the current open season and distribute participants.
        """
        if not self.open_season:
            logging.warning("No open season found.")
            return

        participants = self.get_ranked_participants()
        players_per_league = self.get_players_per_league(participants_count)
        leagues = [self.create_league(level) for level in range(1, len(players_per_league) + 1)]

        self.populate_leagues(leagues, players_per_league, participants)

    @staticmethod
    def populate_leagues(leagues: List[League], players_per_league, participants: List[PlayerProfile]):
        """
        Populate leagues with participants based on their rankings.
        """
        league_index = 0
        for participant in participants:
            for member_count in len(players_per_league[league_index]):
                leagues[league_index].members.add(participant)
                logging.info(f"Added {participant.profile_name} to league {leagues[league_index].level}")
                league_index = (league_index + 1) % len(leagues)

    def get_ranked_participants(self) -> List[dict]:
        """Order participants based on registration and previous participation."""
        participants = get_registered_participants()
        previously_registered = self.get_previous_season_participants(participants)
        new_participants = list(set(participants) - set(previously_registered))

        # Shuffle new participants to mix them up randomly.
        shuffle(new_participants)

        sorted_participants = self.order_previous_season_participants(previously_registered)
        return sorted_participants + new_participants

    @staticmethod
    def get_previous_season_participants(participants: List[PlayerProfile]) -> List[PlayerProfile]:
        """Get participants who were registered in the previous season."""
        previous_season = get_previous_season()
        if not previous_season:
            logging.info("No previous season found.")
            return []
        return [p for p in participants if p in previous_season.participants.all()]

    @staticmethod
    def apply_promotion(participants: List[Dict]) -> List[Dict]:
        """Apply promotion logic to the participants list."""
        # Promote players by swapping their positions if certain conditions are met.
        for index, current in enumerate(participants[1:], start=1):
            previous = participants[index - 1]
            if previous['is_last'] and current['league'] - 1 == previous['league']:
                participants[index], participants[index - 1] = participants[index - 1], participants[index]
        return participants

    def order_previous_season_participants(self, participants: List[PlayerProfile]) -> List[Dict]:
        """Order participants based on their previous season performance."""
        default_list = []
        for p in participants:
            league_info = get_previous_season_result(p)
            if league_info and league_info['league']:
                default_list.append({
                    'name': p.profile_name,
                    'league': league_info['league'].level,
                    'position': league_info['position'],
                    'is_last': league_info['is_last']
                })
        sorted_list = sorted(default_list, key=lambda x: (x['league'], x['position']))
        return self.apply_promotion(sorted_list)
