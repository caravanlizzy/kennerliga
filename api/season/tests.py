from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile
from season.models import Season, SeasonParticipant
from season.services import create_next, open_new, close_running
from season_manager import start_new_season

class SeasonManagerTest(TestCase):
    def test_start_new_season_closes_running_season(self):
        # Create a running season
        running_season = Season.objects.create(year=2025, month=11, status=Season.SeasonStatus.RUNNING)
        # Create an open season
        open_season = Season.objects.create(year=2025, month=12, status=Season.SeasonStatus.OPEN)
        
        start_new_season()
        
        running_season.refresh_from_db()
        open_season.refresh_from_db()
        
        self.assertEqual(running_season.status, Season.SeasonStatus.DONE)
        self.assertEqual(open_season.status, Season.SeasonStatus.RUNNING)

class SeasonLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        
    def test_season_lifecycle(self):
        # Create a running season
        season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        
        # Close it
        close_running(season)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.DONE)
        
        # Create next (OPEN)
        next_season = create_next(season)
        self.assertEqual(next_season.year, 2026)
        self.assertEqual(next_season.month, 2)
        self.assertEqual(next_season.status, Season.SeasonStatus.OPEN)
        
        # Open it (RUNNING)
        opened = open_new()
        self.assertEqual(opened.id, next_season.id)
        self.assertEqual(opened.status, Season.SeasonStatus.RUNNING)

class SeasonAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = PlayerProfile.objects.create(user=self.user, profile_name='Test Profile')
        self.client.force_authenticate(user=self.user)
        self.season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.OPEN)

    def test_register_for_season(self):
        response = self.client.post('/api/season/register/')
        self.assertEqual(response.status_code, 200) # Response is 200 with message
        self.assertTrue(SeasonParticipant.objects.filter(season=self.season, profile=self.profile).exists())
