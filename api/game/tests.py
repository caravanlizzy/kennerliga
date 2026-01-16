from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import Game, SelectedGame, ResultConfig, StartingPointSystem

class GameAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.platform = Platform.objects.create(name='BGA')
        self.season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        self.profile = PlayerProfile.objects.create(user=self.user, profile_name='Admin Profile')
        self.participant = SeasonParticipant.objects.create(season=self.season, profile=self.profile, rank=1)
        
        self.league = League.objects.create(season=self.season, level=1, status=LeagueStatus.PICKING)
        self.league.members.add(self.participant)
        self.league.active_player = self.participant
        self.league.save()
        
        self.sps = StartingPointSystem.objects.create(id=1, code='FIXED', description='Fixed points')
        self.game = Game.objects.create(name='Catan', min_players=1, max_players=4, platform=self.platform)
        ResultConfig.objects.create(game=self.game, has_points=True, starting_points_system=self.sps)

    def test_get_games(self):
        response = self.client.get('/api/game/games/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filter_games_for_selection(self):
        # Create a game that should not be used for selection
        game2 = Game.objects.create(name='Old Game', min_players=1, max_players=4, platform=self.platform, selectable=False)
        
        # Regular request
        response = self.client.get('/api/game/games/')
        self.assertEqual(response.status_code, 200)
        game_names = [g['name'] for g in response.data]
        self.assertIn('Catan', game_names)
        self.assertNotIn('Old Game', game_names)
        
        # Admin request with manage_only=true
        response = self.client.get('/api/game/games/?manage_only=true')
        self.assertEqual(response.status_code, 200)
        game_names = [g['name'] for g in response.data]
        self.assertIn('Catan', game_names)
        self.assertIn('Old Game', game_names)

    def test_select_game(self):
        data = {
            "game": self.game.id,
            "league": self.league.id,
            "profile": self.profile.id,
            "selected_options": []
        }
        response = self.client.post('/api/game/selected-games/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SelectedGame.objects.count(), 1)
        self.assertTrue(response.data['is_selectable'])
        
        # Select another game
        game2 = Game.objects.create(name='Catan 2', min_players=1, max_players=4, platform=self.platform)
        data['game'] = game2.id
        response = self.client.post('/api/game/selected-games/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['is_selectable'])
        
        # Check the first game again - it should NOT be selectable anymore
        first_game_id = SelectedGame.objects.order_by('id').first().id
        response = self.client.get(f'/api/game/selected-games/{first_game_id}/')
        self.assertFalse(response.data['is_selectable'])

        self.league.refresh_from_db()
        self.assertEqual(self.league.status, LeagueStatus.BANNING)
