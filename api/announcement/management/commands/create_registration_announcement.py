from django.core.management.base import BaseCommand
from django.utils import timezone
from announcement.models import Announcement
from season.queries import get_open_season
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create a registration announcement 1 week before the next month'

    def handle(self, *args, **options):
        open_season = get_open_season()
        if not open_season:
            self.stdout.write(self.style.WARNING("No open season found. Cannot create announcement."))
            return

        # Start of the next month (when the open season should start)
        next_month_start = open_season.season_start_time
        
        # Registration announcement should be visible from 1 week before
        visible_from = next_month_start - timedelta(days=7)
        # It should be visible until the season starts
        visible_until = next_month_start

        title = f"Sign Up Season {open_season.month}"
        
        # Check if announcement already exists
        exists = Announcement.objects.filter(
            type=Announcement.AnnouncementType.REGISTER,
            title=title,
            visible_until=visible_until
        ).exists()

        if exists:
            self.stdout.write(self.style.SUCCESS(f"Announcement '{title}' already exists."))
            return

        Announcement.objects.create(
            type=Announcement.AnnouncementType.REGISTER,
            title=title,
            content="",  # Based on screenshot, content was empty
            visible_from=visible_from,
            visible_until=visible_until
        )

        self.stdout.write(self.style.SUCCESS(f"Created registration announcement for {open_season.name}"))
