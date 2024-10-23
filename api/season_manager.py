import logging
from random import shuffle
from typing import List, Dict, Union, Optional

from league.models import League, LeagueResult
from season.models import Season
from season.service import get_running_season, get_open_season, get_leagues, get_previous_season, \
    get_registered_participants
from user.models import PlayerProfile


class SeasonManager:
    def __init__(self):
        self.current_season = get_running_season()
        self.open_season = get_open_season()

    @staticmethod
    def get_new_month_year(current_month: int, current_year: int) -> (int, int):
        """
        Calculate the next month and year based on the current month and year.
        If the current month is December (12), the next month will be January (1) and the year will increment by 1.
        Otherwise, the month will simply increment by 1, and the year will remain the same.

        :param current_month: The current month of the season (1-12)
        :param current_year: The current year of the season
        :return: A tuple (new_month, new_year)
        """
        if current_month == 12:
            new_month = 1
            new_year = current_year + 1
        else:
            new_month = current_month + 1
            new_year = current_year

        return new_month, new_year

    # --- Season Management Functions ---
    def refresh_season_data(self):
        """Refresh the current and open season data."""
        self.current_season = get_running_season()
        self.open_season = get_open_season()

    def close_running_season(self):
        """Close the current running season."""
        if self.current_season:
            self.current_season.status = Season.SeasonStatus.DONE
            self.current_season.save()
        else:
            logging.warning("No running season found to close.")

    def open_new_season(self):
        """Open a new season for the current open season."""
        if self.open_season:
            self.open_season.status = Season.SeasonStatus.RUNNING
            self.open_season.save()
            logging.info(f"Season {self.open_season.year}-{self.open_season.month} started.")
        else:
            logging.warning("No open season found to start.")

    def start_new_season(self):
        """Start a new season by closing the current one and opening a new one."""
        self.create_leagues()
        self.close_running_season()
        self.open_new_season()

    def open_registration(self):
        """Open registration for the current running season."""
        if self.current_season:
            self.current_season.status = Season.SeasonStatus.OPEN
            self.current_season.save()
            logging.info(f"Registration opened for season {self.current_season.year}-{self.current_season.month}.")
        else:
            logging.warning("No running season available for registration.")

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

    @staticmethod
    def register_participant(user):
        current_season = get_open_season()
        if current_season:
            current_season.participants.add(user.profile)

    # --- League Management Functions ---

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

    def create_leagues(self):
        """Create leagues for the current open season and distribute participants."""
        if not self.open_season:
            logging.warning("No open season found.")
            return

        participants = get_registered_participants()
        players_per_league = self.get_players_per_league(len(participants))
        leagues = [self.create_league(level) for level in range(1, len(players_per_league) + 1)]
        print(leagues)

        self.populate_leagues(leagues, players_per_league)

    @staticmethod
    def populate_leagues(leagues: List[League], players_per_league: List[int]):
        """Populate leagues with participants based on their rankings."""
        participants = get_registered_participants()
        participant_counter = 0
        for league_index, league in enumerate(leagues):
            for _ in range(players_per_league[league_index]):
                next_participant = participants[participant_counter]
                league.members.add(next_participant)  # Assuming league.members is a ManyToManyField or similar
                logging.info(f"Added {next_participant.profile_name} to league {league.level}")
                participant_counter += 1

    # --- Participant and League Interaction ---

    @property
    def participants(self):
        return self.current_season.participants

    @staticmethod
    def get_players_per_league(participants_amount: int) -> List[int]:
        """Calculate how many players should be in each league based on the total number of participants."""
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

    def get_ranked_participants(self) -> List[dict]:
        """Order participants based on registration and previous participation."""
        participants = get_registered_participants()
        previously_registered = self.get_previous_season_participants(participants)
        new_participants = [p for p in participants if p not in previously_registered]

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

    # --- Player Performance and League Assignment Functions ---

    @staticmethod
    def get_last_participation(player_profile: PlayerProfile) -> Season:
        """Retrieves the last season in which the player participated."""
        return Season.objects.filter(participants=player_profile).order_by('-year', '-month').first()

    @staticmethod
    def find_player_profile_league(player_profile: PlayerProfile, season: Season) -> Union[League, None]:
        """Find the league for a player profile in a given season."""
        try:
            return get_leagues(season).get(members=player_profile)
        except League.DoesNotExist:
            print('Profile did not participate in this season')
            return None

    @staticmethod
    def get_league_position(player_profile: PlayerProfile, league: League):
        """Retrieves the league position or points of the given player in the specified league."""
        try:
            result = LeagueResult.objects.filter(league=league, profile=player_profile).first()

            if result:
                return result.league_points  # Or whatever defines 'position'
            else:
                logging.info(f'No league result found for player {player_profile} in league {league}')
                return None

        except Exception as e:
            logging.error(f"Error while retrieving league position: {e}")
            return None

    @staticmethod
    def is_last(player_profile: PlayerProfile, league: League) -> bool:
        """Checks if the player is in the last position within the league."""
        try:
            league_result = LeagueResult.objects.get(league=league, profile=player_profile)
            return league_result.position == league.members.count()
        except LeagueResult.DoesNotExist:
            logging.warning(f'No league result found for {player_profile} in league {league}.')
            return False

    def get_previous_season_result(self, player_profile: PlayerProfile) -> Optional[Dict]:
        """Retrieves the previous season's league and position for the player profile."""
        previous_season = get_previous_season()
        last_participation = self.get_last_participation(player_profile)

        if previous_season != last_participation:
            return None

        previous_league = self.find_player_profile_league(player_profile, previous_season)
        previous_position = self.get_league_position(player_profile, previous_league) if previous_league else None
        previous_is_last = self.is_last(player_profile, previous_league)

        return {
            "league": previous_league,
            "position": previous_position,
            "is_last": previous_is_last,
        }

    def order_previous_season_participants(self, participants: List[PlayerProfile]) -> List[Dict]:
        """Order participants based on their previous season performance."""
        default_list = []
        for p in participants:
            league_info = self.get_previous_season_result(p)
            if league_info and league_info['league']:
                default_list.append({
                    'name': p.profile_name,
                    'league': league_info['league'].level,
                    'position': league_info['position'],
                    'is_last': league_info['is_last']
                })
        sorted_list = sorted(default_list, key=lambda x: (x['league'], x['position']))
        return self.apply_promotion(sorted_list)

    @staticmethod
    def apply_promotion(participants: List[Dict]) -> List[Dict]:
        """Apply promotion logic to the participants list, making a copy to avoid in-place modifications."""
        participants_copy = participants.copy()

        for index, current in enumerate(participants_copy[1:], start=1):
            previous = participants_copy[index - 1]
            if previous['is_last'] and current['league'] - 1 == previous['league']:
                participants_copy[index], participants_copy[index - 1] = participants_copy[index - 1], \
                    participants_copy[index]
        return participants_copy
