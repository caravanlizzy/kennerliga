import logging
from league.models import League
from season.models import Season
from season.queries import get_running_season, get_open_season
from random import shuffle
from typing import List, Dict, Optional
from season.queries import get_previous_season
from user.models import PlayerProfile

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



class RankingService:
    def __init__(self, season: Season):
        self.season = season

    def rank_participants(self, participants: List[PlayerProfile]) -> List[Dict]:
        prev_participants = self.get_previous_participants(participants)
        new_participants = [p for p in participants if p not in prev_participants]

        shuffle(new_participants)
        sorted_prev = self.order_previous(prev_participants)
        return sorted_prev + new_participants

    def get_previous_participants(self, participants: List[PlayerProfile]) -> List[PlayerProfile]:
        prev_season = get_previous_season()
        if not prev_season:
            return []
        return [p for p in participants if p in prev_season.participants.all()]

    def get_previous_result(self, profile: PlayerProfile) -> Optional[Dict]:
        prev_season = get_previous_season()
        last_season = Season.objects.filter(participants=profile).order_by('-year', '-month').first()
        if prev_season != last_season:
            return None

        try:
            league = League.objects.get(season=prev_season, members=profile)
        except League.DoesNotExist:
            return None

        result = LeagueResult.objects.filter(league=league, profile=profile).first()
        return {
            "league": league.level,
            "position": result.league_points if result else None,
            "is_last": (result and result.position == league.members.count())
        }

    def order_previous(self, participants: List[PlayerProfile]) -> List[Dict]:
        data = []
        for p in participants:
            info = self.get_previous_result(p)
            if info:
                data.append({
                    "name": p.profile_name,
                    "league": info["league"],
                    "position": info["position"],
                    "is_last": info["is_last"],
                })
        sorted_list = sorted(data, key=lambda x: (x["league"], x["position"]))
        return self.apply_promotion(sorted_list)

    @staticmethod
    def apply_promotion(participants: List[Dict]) -> List[Dict]:
        # Apply simple promotion/relegation rule
        participants_copy = participants.copy()
        for i, current in enumerate(participants_copy[1:], start=1):
            prev = participants_copy[i - 1]
            if prev["is_last"] and current["league"] - 1 == prev["league"]:
                participants_copy[i], participants_copy[i - 1] = prev, current
        return participants_copy
