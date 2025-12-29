from django.core.management.base import BaseCommand
from game.models import SelectedGame
from league.models import League
from services.standings_snapshot import rebuild_game_snapshot, rebuild_league_snapshot

class Command(BaseCommand):
    help = 'Rebuilds all game and league standings'

    def handle(self, *args, **options):
        self.stdout.write("Rebuilding game standings...")
        selected_games = SelectedGame.objects.all().select_related('league')
        total_games = selected_games.count()
        for i, sg in enumerate(selected_games):
            rebuild_game_snapshot(sg)
            if (i + 1) % 10 == 0:
                self.stdout.write(f"Processed {i + 1}/{total_games} games")
        self.stdout.write(self.style.SUCCESS(f"Successfully rebuilt {total_games} game standings"))

        self.stdout.write("Rebuilding league standings...")
        leagues = League.objects.all()
        total_leagues = leagues.count()
        for i, league in enumerate(leagues):
            rebuild_league_snapshot(league)
            if (i + 1) % 5 == 0:
                self.stdout.write(f"Processed {i + 1}/{total_leagues} leagues")
        self.stdout.write(self.style.SUCCESS(f"Successfully rebuilt {total_leagues} league standings"))
