from django.core.management.base import BaseCommand

from season_manager import start_new_season


class Command(BaseCommand):
    """
    Management command to start a new season.
    It checks if the current season is finished and then initiates the new season.
    """
    help = "Starts a new season if the current one is finished"

    def handle(self, *args, **options):
        start_new_season()
        self.stdout.write(self.style.SUCCESS("New season started successfully"))
