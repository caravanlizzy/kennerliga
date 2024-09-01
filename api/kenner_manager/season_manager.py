from datetime import datetime, timedelta
from typing import List

from season.models import Season
from user.models import PlayerProfile


class SeasonManager:

    @staticmethod
    def get_running_season():
        return Season.objects.filter(status=Season.SeasonStatus.RUNNING).first()
        # return Season.objects.order_by('-year', '-month').first()

    @staticmethod
    def get_open_season():
        return Season.objects.filter(status=Season.SeasonStatus.OPEN).first()

    @staticmethod
    def get_new_month_year(month, year):
        new_month = month + 1
        new_year = year
        if new_month == 13:
            new_year += 1
            new_month = 1
        return new_month, new_year

    def create_next_season(self):
        current_season = self.get_running_season()
        if not current_season:
            print("No seasons created so far.")
            return
        new_month, new_year = self.get_new_month_year(current_season.month, current_season.year)
        new_season = Season(year=new_year, month=new_month)
        new_season.save()
        print(f"Next season created: {new_season.year}-{new_season.month}")

    def start_season(self):
        season = self.get_running_season()
        season.status = Season.SeasonStatus.RUNNING
        season.save()

    def open_registration(self):
        season = self.get_running_season()
        season.status = Season.SeasonStatus.OPEN
        season.save()

    @staticmethod
    def check_new_season():
        today = datetime.today()
        first_day_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_this_month = first_day_next_month - timedelta(days=1)
        days_left = (last_day_this_month - today).days
        return days_left == 7

    @staticmethod
    def get_player_order(season_name):
        participants = Season.objects.filter(year=season_name).participants.all()

    def get_registered_participant_count(self):
        season = self.get_open_season()
        if season:
            return season.participants.count()
        else:
            print("No open season found.")
            return 0

    def get_registered_participants(self):
        season = self.get_open_season()
        if season:
            return season.participants.all()
        else:
            print("No open season found.")
            return []

    # the distribution of the leagues can be obtained from this order
    def order_participants(self) -> List[PlayerProfile]:
        participants = self.get_registered_participants()
        # order particpiants here...
        ordered_participants = participants
        return ordered_participants
