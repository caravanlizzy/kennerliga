from datetime import datetime, timedelta

from season.models import Season


class Organize:

    @staticmethod
    def get_current_season():
        return Season.objects.order_by('-year', '-month').first()

    def get_new_month_year(month, year):
        new_month = month + 1
        new_year = year
        if new_month == 13:
            new_year += 1
            new_month = 1
        return [new_month, new_year]

    def create_season(self):
        current_season = self.get_current_season()
        if not current_season:
            print("No seasons created so far.")
            return
        new_month, new_year = self.get_new_month_year(current_season.month, current_season.year)
        new_season = Season(year=new_year, month=new_month)
        new_season.save()

    def start_season(self):
        season = self.get_current_season()
        season.status = Season.SeasonStatus.RUNNING
        season.save()

    def open_season(self):
        season = self.get_current_season()
        season.status = Season.SeasonStatus.OPEN
        season.save()

    @staticmethod
    def check_new_season():
        today = datetime.today()
        first_day_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_this_month = first_day_next_month - timedelta(days=1)
        days_left = (last_day_this_month - today).days
        return days_left == 7
