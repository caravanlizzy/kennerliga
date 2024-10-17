from datetime import datetime, timedelta
from typing import List

from season.models import Season
from season.service import SeasonService
from user.models import PlayerProfile
from user.profile_service import ProfileService


class SeasonManager:

    @staticmethod
    def get_new_month_year(month, year):
        new_month = month + 1
        new_year = year
        if new_month == 13:
            new_year += 1
            new_month = 1
        return new_month, new_year

    def create_next_season(self):
        current_season = SeasonService.get_running_season()
        if not current_season:
            print("No seasons created so far.")
            return
        new_month, new_year = self.get_new_month_year(current_season.month, current_season.year)
        new_season = Season(year=new_year, month=new_month)
        new_season.save()
        print(f"Next season created: {new_season.year}-{new_season.month}")

    @staticmethod
    def start_season():
        season = SeasonService.get_running_season()
        season.status = Season.SeasonStatus.RUNNING
        season.save()

    @staticmethod
    def open_registration():
        season = SeasonService.get_running_season()
        season.status = Season.SeasonStatus.OPEN
        season.save()

    @staticmethod
    def check_new_season():
        today = datetime.today()
        first_day_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_this_month = first_day_next_month - timedelta(days=1)
        days_left = (last_day_this_month - today).days
        return days_left == 7

        # the distribution of the leagues can be obtained from this order

    @staticmethod
    def get_previous_season_participants(participants: List[PlayerProfile]) -> List[PlayerProfile]:
        previous_season = SeasonService.get_previous_season()
        if not previous_season:
            return []  # Return an empty list if no previous season exists

        previous_participants = set(previous_season.participants.all())
        return [p for p in participants if p in previous_participants]

    @staticmethod
    def apply_promotion(participants):
        for (index, p) in enumerate(participants):
            if index == 0:
                continue
            previous = participants[index - 1]
            if previous['is_last'] and p.league - 1 == previous.league:
                participants[index], participants[index - 1] = participants[index - 1], participants[index]
        return participants

    def order_previous_season_participants(self, participants: List[PlayerProfile]) -> List[Dict]:
        default_list = []
        for p in participants:
            league_info = ProfileService.get_previous_season_result(p)
            if league_info:
                league = league_info[0]
                position = league_info[1]
                default_list.append({
                    'name': p.profile_name,
                    'league': league.level,
                    'position': position,
                    'is_last': ProfileService.is_last(p)
                })

        sorted_list = sorted(default_list, key=lambda x: (x['league'], x['position']))
        promoted_list = self.apply_promotion(sorted_list)
        return promoted_list

    def order_participants(self) -> List[PlayerProfile]:
        participants = SeasonService.get_registered_participants()
        previously_registered = self.get_previous_season_participants(participants)
        new_participants = set(participants) - set(previously_registered)
        ordered_participants = participants
        return ordered_participants
