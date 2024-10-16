from season.models import Season


class SeasonService:
    @staticmethod
    def get_running_season():
        return Season.objects.filter(status=Season.SeasonStatus.RUNNING).first()

    @staticmethod
    def get_open_season():
        return Season.objects.filter(status=Season.SeasonStatus.OPEN).first()

    @staticmethod
    def get_previous_season():
        return Season.objects.filter(status=Season.SeasonStatus.DONE).last()

    @staticmethod
    def get_participants(season_name):
        return Season.objects.filter(year=season_name).participants.all()

    @staticmethod
    def get_leagues():
        return Season.league_set.all()  # Reverse foreign key access

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
