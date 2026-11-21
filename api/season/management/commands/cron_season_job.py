from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.core.management import call_command
from django.core.management.base import BaseCommand


def get_berlin_today(target_datetime=None):
    """
    Returns today's date in Europe/Berlin timezone.
    """
    if target_datetime is None:
        target_datetime = datetime.now(ZoneInfo("Europe/Berlin"))
    if target_datetime.tzinfo is None:
        target_datetime = target_datetime.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    else:
        target_datetime = target_datetime.astimezone(ZoneInfo("Europe/Berlin"))
    return target_datetime.date()


def is_seven_days_before_new_month(date_obj):
    """
    Checks if date_obj is exactly 7 days before the 1st of the next month.
    """
    return (date_obj + timedelta(days=7)).day == 1


def is_first_day_of_month(date_obj):
    """
    Checks if date_obj is the first day of the month.
    """
    return date_obj.day == 1


class Command(BaseCommand):
    help = (
        "Cron job task for season lifecycle management. "
        "Checks Berlin date: runs open_next_season if 7 days before next month, "
        "or start_new_season if on the 1st day of the month."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Override current date (format YYYY-MM-DD) for testing or manual runs",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        if date_str:
            try:
                today_berlin = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stderr.write(
                    self.style.ERROR(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
                )
                return
        else:
            today_berlin = get_berlin_today()

        self.stdout.write(f"Evaluating season cron job for date: {today_berlin} (Europe/Berlin)")

        if is_seven_days_before_new_month(today_berlin):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Date {today_berlin} is 7 days before the new month. Running open_next_season..."
                )
            )
            call_command("open_next_season", stdout=self.stdout, stderr=self.stderr)
        elif is_first_day_of_month(today_berlin):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Date {today_berlin} is the 1st day of the month. Running start_new_season..."
                )
            )
            call_command("start_new_season", stdout=self.stdout, stderr=self.stderr)
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Date {today_berlin} is neither 7 days before next month nor the 1st of the month. No action required."
                )
            )
