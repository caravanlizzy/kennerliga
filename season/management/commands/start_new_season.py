from django.core.management import BaseCommand

from season.models import Season


class Command(BaseCommand):
    help = "Process the start of a new season"

    def handle(self, *args, **options):
        if self.can_season_start():
            running_season = self.get_running_season()[0]
            open_season = self.get_open_season()
            running_season.status = Season.SeasonStatus.DONE
            running_season.save()
            open_season.status = Season.SeasonStatus.RUNNING
            open_season.save()

    def can_season_start(self):
        open_season = self.get_open_season()
        if len(open_season) > 1:
            return False
        if len(self.get_running_season()) > 1:
            return False
        if len(open_season[0].participants) < 6:
            return False

    @staticmethod
    def get_running_season():
        return Season.objects.filter(status=Season.SeasonStatus.RUNNING)

    @staticmethod
    def get_open_season():
        return Season.objects.filter(status=Season.SeasonStatus.OPEN)
