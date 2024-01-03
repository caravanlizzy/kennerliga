from django.core.management import BaseCommand
from django.db.models import Q

from season.models import Season
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create the next season'

    def handle(self, *args, **options):
        current_season = self.get_current_season()
        if len(self.get_non_done_seasons()) > 1:
            logger.error(
                'There are more than 1 seasons with a state SeasonStatus.NEXT, SeasonStatus.ANNOUNCED or SeasonStatus.RUNNING')
        elif current_season:
            self.create_new_season(current_season)
        else:
            logger.error('Cannot create new season since no active season has been found.')

    @staticmethod
    def create_new_season(current_season):
        if current_season.month == 12:
            new_year = current_season.year + 1
            new_month = 1
        else:
            new_year = current_season.year
            new_month = current_season.month + 1
        new_season = Season(year=new_year, month=new_month)
        current_season.status = Season.SeasonStatus.DONE
        new_season.save()
        return new_season

    @staticmethod
    def get_current_season():
        current_season = Season.objects.filter(status=Season.SeasonStatus.RUNNING)
        if not current_season:
            logger.error('No running season found.')
        elif len(current_season) > 1:
            logger.error('More than one active season found')
        return current_season[0]

    @staticmethod
    def get_non_done_seasons():
        return Season.objects.filter(~Q(status=Season.SeasonStatus.DONE))
