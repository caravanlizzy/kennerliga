from django.core.management.base import BaseCommand
from services.elo import rebuild_all_elo


class Command(BaseCommand):
    help = "Recalculates all player Elo ratings from historical match results in chronological order."

    def handle(self, *args, **options):
        self.stdout.write("Recalculating Elo ratings from match history...")
        count = rebuild_all_elo()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully recalculated Elo ratings across {count} matches.")
        )
