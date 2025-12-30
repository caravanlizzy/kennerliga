from django.test import TestCase
from season.models import Season
from season_manager import SeasonManager

class SeasonManagerTest(TestCase):
    def test_start_new_season_closes_running_season(self):
        # Create a running season
        running_season = Season.objects.create(year=2025, month=11, status=Season.SeasonStatus.RUNNING)
        # Create an open season
        open_season = Season.objects.create(year=2025, month=12, status=Season.SeasonStatus.OPEN)
        
        manager = SeasonManager()
        manager.start_new_season()
        
        running_season.refresh_from_db()
        open_season.refresh_from_db()
        
        self.assertEqual(running_season.status, Season.SeasonStatus.DONE)
        self.assertEqual(open_season.status, Season.SeasonStatus.RUNNING)
