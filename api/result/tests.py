from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import Game, SelectedGame, ResultConfig, TieBreaker, StartingPointSystem
from result.models import Result

class ResultAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.platform = Platform.objects.create(name='BGA')
        self.season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        self.profile = PlayerProfile.objects.create(user=self.user, profile_name='Admin Profile')
        self.participant = SeasonParticipant.objects.create(season=self.season, profile=self.profile, rank=1)
        
        self.league = League.objects.create(season=self.season, level=1, status=LeagueStatus.PLAYING)
        self.league.members.add(self.participant)
        self.league.save()
        
        self.sps = StartingPointSystem.objects.create(id=1, code='FIXED', description='Fixed points')
        self.game = Game.objects.create(name='Catan', min_players=1, max_players=4, platform=self.platform)
        self.config = ResultConfig.objects.create(game=self.game, has_points=True, starting_points_system=self.sps)
        self.selected_game = SelectedGame.objects.create(game=self.game, league=self.league, profile=self.profile)

    def test_submit_match_result(self):
        # Create another player as MatchResultViewSet requires at least 2 results
        user2 = User.objects.create(username='user2')
        profile2 = PlayerProfile.objects.create(user=user2, profile_name='Profile 2')
        participant2 = SeasonParticipant.objects.create(season=self.season, profile=profile2, rank=2)
        self.league.members.add(participant2)

        data = {
            "selected_game": self.selected_game.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1
                },
                {
                    "player_profile": profile2.id,
                    "points": 8,
                    "starting_position": 2
                }
            ]
        }
        response = self.client.post('/api/result/match-results/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Result.objects.count(), 2)
        
        result = Result.objects.get(player_profile=self.profile)
        self.assertEqual(result.points, 10)
        self.assertEqual(result.position, 1)
        
    def test_submit_match_result_with_tie(self):
        # Create another player
        user2 = User.objects.create(username='user2')
        profile2 = PlayerProfile.objects.create(user=user2, profile_name='Profile 2')
        participant2 = SeasonParticipant.objects.create(season=self.season, profile=profile2, rank=2)
        self.league.members.add(participant2)
        
        tb = TieBreaker.objects.create(result_config=self.config, name='TB1', order=1)
        
        data = {
            "selected_game": self.selected_game.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1
                },
                {
                    "player_profile": profile2.id,
                    "points": 10,
                    "starting_position": 2
                }
            ]
        }
        # First submission with equal points
        response = self.client.post('/api/result/match-results/', data, format='json')
        # Based on result/views.py:152, it returns 202 ACCEPTED for ties
        self.assertEqual(response.status_code, 202) 
        self.assertIn('tie_groups', response.data)
        
        # Submit with tiebreaker
        data['tiebreaker'] = {"id": tb.id}
        data['results'][0]['tie_breaker_value'] = 5
        data['results'][1]['tie_breaker_value'] = 3
        
        response = self.client.post('/api/result/match-results/', data, format='json')
        self.assertEqual(response.status_code, 201)
        
        res1 = Result.objects.get(player_profile=self.profile)
        res2 = Result.objects.get(player_profile=profile2)
        
        self.assertEqual(res1.position, 1)
        self.assertEqual(res2.position, 2)
        self.assertEqual(res1.decisive_tie_breaker, tb)

    def test_fractional_wins_on_tie(self):
        # Create another player
        user2 = User.objects.create(username='user2')
        profile2 = PlayerProfile.objects.create(user=user2, profile_name='Profile 2')
        participant2 = SeasonParticipant.objects.create(season=self.season, profile=profile2, rank=2)
        self.league.members.add(participant2)

        data = {
            "selected_game": self.selected_game.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1
                },
                {
                    "player_profile": profile2.id,
                    "points": 10,
                    "starting_position": 2
                }
            ]
        }
        # Submission with equal points and NO tie-breakers defined for this game in setUp
        # Actually, let's make sure no tie-breakers exist so it stays a tie.
        TieBreaker.objects.filter(result_config=self.config).delete()

        response = self.client.post('/api/result/match-results/', data, format='json')
        # Since there are no tie-breakers, it should finalize immediately with a tie
        self.assertEqual(response.status_code, 201)

        from league.models import LeagueStanding, GameStanding
        # Check GameStanding for win_share
        gs1 = GameStanding.objects.get(selected_game=self.selected_game, player_profile=self.profile)
        gs2 = GameStanding.objects.get(selected_game=self.selected_game, player_profile=profile2)

        # Both should have 0.5 wins
        self.assertEqual(float(gs1.win_share), 0.5)
        self.assertEqual(float(gs2.win_share), 0.5)

        # Check LeagueStanding for total wins
        ls1 = LeagueStanding.objects.get(league=self.league, player_profile=self.profile)
        ls2 = LeagueStanding.objects.get(league=self.league, player_profile=profile2)

        self.assertEqual(float(ls1.wins), 0.5)
        self.assertEqual(float(ls2.wins), 0.5)
