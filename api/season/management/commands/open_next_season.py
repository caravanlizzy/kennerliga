import calendar
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from season_manager import open_next_season


class Command(BaseCommand):
    help = "Open the next season for registration and create registration announcements"

    def add_arguments(self, parser):
        parser.add_argument(
            "--check-7-days",
            action="store_true",
            help="Only open if today is 7 days before the end of the month",
        )

    def handle(self, *args, **options):
        if options.get("check_7_days"):
            today = timezone.now().date()
            _, last_day = calendar.monthrange(today.year, today.month)
            days_until_end = last_day - today.day
            is_seven_days_before = (
                days_until_end == 7 or (today + timedelta(days=7)).day == 1
            )
            if not is_seven_days_before:
                self.stdout.write(
                    self.style.WARNING(
                        f"Today ({today}) is not 7 days before the end of the month (day {today.day} of {last_day}). Skipping."
                    )
                )
                return

        season = open_next_season()
        if not season:
            self.stdout.write(
                self.style.WARNING("No season in NEXT status found to open for registration.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Season {season.name} is now open for registration.")
        )
