from django.core.management.base import BaseCommand

from season_manager import SeasonManager


class Command(BaseCommand):
    help = "Starts a new season if the current one is finished"

    def handle(self, *args, **options):
        manager = SeasonManager()
        manager.start_new_season()
        self.stdout.write(self.style.SUCCESS("New season started successfully"))
