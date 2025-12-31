import logging
from league.models import League, LeagueResult
from season.models import Season
from season.queries import get_running_season, get_open_season
from random import shuffle
from typing import List, Dict, Optional, Any
from season.queries import get_previous_season
from user.models import PlayerProfile

class SeasonService:
    """
    Service class for handling operations related to a season.

    This class provides various methods to manage the lifecycle and operations
    of a "Season" entity such as closing the running season, opening a new season,
    and creating leagues for participants. It supports managing seasonal transitions,
    updating season statuses, and organizing participants into leagues.
    """
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
    """
    Provides functionality to manage and rank participants based on their previous participation in competitive seasons,
    with mechanisms for handling new participants and promoting or relegating participants between leagues.

    This class is intended to rank a list of participants, combining previously known participants with new ones, applying
    ordering logic to the previous participants, shuffling new participants to ensure unbiased placement, and then merging
    both groups. The system also includes methods for retrieving historical participation data and performing processing
    on league promotion or relegation. The service is particularly useful for competitive systems with hierarchical league
    structures.
    """
    def __init__(self, season: Season):
        self.season = season

    def rank_participants(self, participants: List[Any]) -> List[Any]:
        """
        Ranks participants based on their previous participation and randomizes the order of new participants.

        The method separates previously known participants from new ones. Previously known participants are ordered
        using a custom ordering function, while new participants are shuffled to avoid any implicit ordering by
        registration timestamps. The method then creates a fully ranked list by combining ordered previous participants
        and shuffled new participants.

        Parameters:
            participants (List[Any]): List of participants to rank. Participants can be objects or any type
            implementing the required comparison logic.

        Returns:
            List[Any]: A combined list of previously ordered participants and newly shuffled participants.
        """
        # participant_profiles = [self._to_profile(p) for p in participants]
        # participant_profiles = [p for p in participant_profiles if p is not None]

        prev_participants = self.get_previous_participants(participants)
        new_participants = [p for p in participants if p not in prev_participants]

        # Shuffle participants to avoid ranking by registration timestamp
        shuffle(new_participants)
        sorted_prev = self.order_previous(prev_participants)
        fully_ranked = sorted_prev + new_participants
        for (index, participant) in enumerate(fully_ranked):
            participant.rank = index + 1
            participant.save()
        return fully_ranked

    def get_previous_participants(self, participants) -> List:
        """
        Filters a given list of participants to obtain those who participated in the
        previous season.

        The function retrieves the participants of the previous season and compares
        them with the provided list of participants. It returns only the participants
        who were also part of the previous season. If there is no previous season, an
        empty list is returned.

        Args:
            participants: List of current participants to be filtered.

        Returns:
            List containing only participants who were part of the previous season.
        """
        prev_season = get_running_season()
        if not prev_season:
            return []
        prev_participants = set(prev_season.participants.all())
        return [p for p in participants if p in prev_participants]

    def get_previous_result(self, profile: PlayerProfile) -> Optional[dict]:
        prev_season = get_previous_season()
        last_season = Season.objects.filter(participants=profile).order_by("-year", "-month").first()
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
            "is_last": (result and result.position == league.members.count()),
        }

    def order_previous(self, participants: List[PlayerProfile]) -> List[PlayerProfile]:
        data = []
        for p in participants:
            info = self.get_previous_result(p)
            if info and info["position"] is not None:
                data.append(
                    {
                        "profile": p,
                        "league": info["league"],
                        "position": info["position"],
                        "is_last": info["is_last"],
                    }
                )

        sorted_list = sorted(data, key=lambda x: (x["league"], x["position"]))
        promoted = self.apply_promotion(sorted_list)
        return [row["profile"] for row in promoted]

    @staticmethod
    def apply_promotion(participants: List[dict]) -> List[dict]:
        # Apply simple promotion/relegation rule
        participants_copy = participants.copy()
        for i, current in enumerate(participants_copy[1:], start=1):
            prev = participants_copy[i - 1]
            if prev["is_last"] and current["league"] - 1 == prev["league"]:
                participants_copy[i], participants_copy[i - 1] = prev, current
        return participants_copy
