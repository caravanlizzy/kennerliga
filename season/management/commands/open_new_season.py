from django.core.management import BaseCommand

from season.models import Season
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Open the new season for registration"

    def handle(self, *args, **options):
        next_seasons = Season.objects.filter(status=Season.SeasonStatus.NEXT)
        if not len(next_seasons) == 1:
            logger.error('More than 1 NEXT seasons found')
        else:
            next_season = next_seasons[0]
            next_season.status = Season.SeasonStatus.OPEN
            next_season.save()

