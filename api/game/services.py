import logging
from typing import List
from league.models import League
from season.models import Season
from season.queries import get_running_season, get_open_season, get_registered_participants


class SeasonService:
    def __init__(self, season: Season = None):
        self.season = season or get_running_season()

    def close_running(self):
        if not self.season:
            logging.warning("No running season to close")
            return
        self.season.status = Season.SeasonStatus.DONE
        self.season.save()

    def open_new(self):
        open_season = get_open_season()
        if not open_season:
            logging.warning("No open season found")
            return
        open_season.status = Season.SeasonStatus.RUNNING
        open_season.save()
        return open_season

    def create_next(self) -> Season:
        if not self.season:
            raise ValueError("No running season found")
        new_month, new_year = self._next_month_year(self.season.month, self.season.year)
        new = Season(year=new_year, month=new_month, status=Season.SeasonStatus.OPEN)
        new.save()
        return new

    def open_registration(self):
        if not self.season:
            raise ValueError("No current season")
        self.season.status = Season.SeasonStatus.OPEN
        self.season.save()

    def create_leagues(self, participants: List) -> List[League]:
        players_per_league = self._players_per_league(len(participants))
        leagues = [League.objects.create(season=self.season, level=i + 1)
                   for i in range(len(players_per_league))]
        counter = 0
        for league, size in zip(leagues, players_per_league):
            for _ in range(size):
                league.members.add(participants[counter])
                counter += 1
        return leagues

    @staticmethod
    def _next_month_year(month: int, year: int):
        return (1, year + 1) if month == 12 else (month + 1, year)

    @staticmethod
    def _players_per_league(count: int) -> List[int]:
        league_count, rest = divmod(count, 4)
        players = [4] * league_count
        if rest == 1:
            if league_count > 0:
                players[-1] = 3
            players.append(2)
        elif rest == 2:
            players.append(2)
        elif rest == 3:
            players.append(3)
        return players
