from django.core.management import BaseCommand
from django.db.models import Q

from season.models import Season
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Activate the next season'

    def handle(self, *args, **options):
        current_season = self.get_current_season()
        if current_season:
            self.create_new_season(current_season)




    @staticmethod
    def get_not_done_seasons():
        return list(Season.objects.filter(~Q(status=Season.SeasonStatus.DONE)))
