from django.test import TestCase
from rest_framework.test import APIClient

from season.queries import get_open_season
from user.models import User, PlayerProfile
from season.models import Season, SeasonParticipant
from season.services import create_next_season, start_open_season, close_season, rank_participants, open_registration
from league.models import League, LeagueStanding
from season_manager import start_new_season

class SeasonManagerTest(TestCase):
    def test_start_new_season_closes_running_season(self):
        # Create a running season
        running_season = Season.objects.create(year=2025, month=11, status=Season.SeasonStatus.RUNNING)
        # Create an open season
        open_season = Season.objects.create(year=2025, month=12, status=Season.SeasonStatus.OPEN)
        # Add some participants (at least 2 for _players_per_league to work without IndexError if I'm unlucky)
        p1 = PlayerProfile.objects.create(profile_name='P1')
        p2 = PlayerProfile.objects.create(profile_name='P2')
        SeasonParticipant.objects.create(season=open_season, profile=p1)
        SeasonParticipant.objects.create(season=open_season, profile=p2)
        
        start_new_season()
        
        running_season.refresh_from_db()
        open_season.refresh_from_db()
        
        self.assertEqual(running_season.status, Season.SeasonStatus.DONE)
        self.assertEqual(open_season.status, Season.SeasonStatus.RUNNING)

    def test_start_new_season_no_open_season(self):
        with self.assertRaisesRegex(ValueError, "No open season found to start"):
            start_new_season()

class SeasonLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        
    def test_season_lifecycle(self):
        # Create a running season
        season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        
        # Close it
        close_season(season)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.DONE)
        
        # Create next (NEXT)
        next_season = create_next_season(season)
        self.assertEqual(next_season.year, 2026)
        self.assertEqual(next_season.month, 2)
        self.assertEqual(next_season.status, Season.SeasonStatus.NEXT)
        
        # Open registration (OPEN)
        open_registration(next_season)
        self.assertEqual(next_season.status, Season.SeasonStatus.OPEN)
        
        # Open it (RUNNING)
        open_season = get_open_season()
        opened = start_open_season(open_season)
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

class RankParticipantsTest(TestCase):
    def setUp(self):
        # Setup previous season
        self.prev_season = Season.objects.create(year=2025, month=12, status=Season.SeasonStatus.DONE)
        
        # 4 players in L1
        self.p1 = PlayerProfile.objects.create(profile_name='P1')
        self.p2 = PlayerProfile.objects.create(profile_name='P2')
        self.p3 = PlayerProfile.objects.create(profile_name='P3')
        self.p4 = PlayerProfile.objects.create(profile_name='P4')
        
        # 4 players in L2
        self.p5 = PlayerProfile.objects.create(profile_name='P5')
        self.p6 = PlayerProfile.objects.create(profile_name='P6')
        self.p7 = PlayerProfile.objects.create(profile_name='P7')
        self.p8 = PlayerProfile.objects.create(profile_name='P8')

        # Previous season participants
        self.prev_participants = {}
        for p in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8]:
            self.prev_participants[p.profile_name] = SeasonParticipant.objects.create(season=self.prev_season, profile=p)

        self.l1 = League.objects.create(season=self.prev_season, level=1)
        self.l2 = League.objects.create(season=self.prev_season, level=2)

        # Add participants to leagues
        for p_name in ['P1', 'P2', 'P3', 'P4']:
            self.l1.members.add(self.prev_participants[p_name])
        for p_name in ['P5', 'P6', 'P7', 'P8']:
            self.l2.members.add(self.prev_participants[p_name])

        # L1 standings
        LeagueStanding.objects.create(league=self.l1, player_profile=self.p1, league_points=10)
        LeagueStanding.objects.create(league=self.l1, player_profile=self.p2, league_points=8)
        LeagueStanding.objects.create(league=self.l1, player_profile=self.p3, league_points=6)
        LeagueStanding.objects.create(league=self.l1, player_profile=self.p4, league_points=4) # Last in L1

        # L2 standings
        LeagueStanding.objects.create(league=self.l2, player_profile=self.p5, league_points=10) # Winner L2
        LeagueStanding.objects.create(league=self.l2, player_profile=self.p6, league_points=8)
        LeagueStanding.objects.create(league=self.l2, player_profile=self.p7, league_points=6)
        LeagueStanding.objects.create(league=self.l2, player_profile=self.p8, league_points=4)

        # New season
        self.new_season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.OPEN)
        
        # Participants for new season: all old ones + some new ones
        self.new_p1 = PlayerProfile.objects.create(profile_name='New1')
        self.new_p2 = PlayerProfile.objects.create(profile_name='New2')
        
        self.all_profiles = [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.new_p1, self.new_p2]
        self.participants = []
        for p in self.all_profiles:
            self.participants.append(SeasonParticipant.objects.create(season=self.new_season, profile=p))

    def test_rank_participants_order(self):
        ranked = rank_participants(self.new_season, self.participants)
        
        # Check that we got all back
        self.assertEqual(len(ranked), 10)
        
        # Ranks should be 1 to 10
        self.assertEqual([p.rank for p in ranked], list(range(1, 11)))
        
        # Check order:
        # P1, P2, P3 are L1 top 3. P4 is last in L1. P5 is winner of L2.
        # apply_promotion should swap P4 and P5.
        # Expected order: P1, P2, P3, P5, P4, P6, P7, P8, (New1, New2 in any order)
        
        ranked_profiles = [p.profile for p in ranked]
        self.assertEqual(ranked_profiles[0], self.p1)
        self.assertEqual(ranked_profiles[1], self.p2)
        self.assertEqual(ranked_profiles[2], self.p3)
        self.assertEqual(ranked_profiles[3], self.p5) # Promoted
        self.assertEqual(ranked_profiles[4], self.p4) # Relegated
        self.assertEqual(ranked_profiles[5], self.p6)
        self.assertEqual(ranked_profiles[6], self.p7)
        self.assertEqual(ranked_profiles[7], self.p8)
        
        # New players should be at the end
        self.assertIn(ranked_profiles[8], [self.new_p1, self.new_p2])
        self.assertIn(ranked_profiles[9], [self.new_p1, self.new_p2])
