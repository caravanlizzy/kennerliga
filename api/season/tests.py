from django.test import TestCase
from rest_framework.test import APIClient

from season.queries import get_open_season
from user.models import User, PlayerProfile
from season.models import Season, SeasonParticipant
from season.services import (
    create_next_season,
    start_open_season,
    close_season,
    rank_participants,
    open_registration,
    apply_promotion,
)
from league.models import League, LeagueStanding
from season_manager import start_new_season


class SeasonManagerTest(TestCase):
    def test_start_new_season_closes_running_season(self):
        # Create a running season
        running_season = Season.objects.create(
            year=2025, month=11, status=Season.SeasonStatus.RUNNING
        )
        # Create an open season
        open_season = Season.objects.create(
            year=2025, month=12, status=Season.SeasonStatus.OPEN
        )
        # Add some participants (at least 2 for _players_per_league to work without IndexError if I'm unlucky)
        p1 = PlayerProfile.objects.create(profile_name="P1")
        p2 = PlayerProfile.objects.create(profile_name="P2")
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
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_authenticate(user=self.user)

    def test_season_lifecycle(self):
        # Create a running season
        season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )

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
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = PlayerProfile.objects.create(
            user=self.user, profile_name="Test Profile"
        )
        self.client.force_authenticate(user=self.user)
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.OPEN
        )

    def test_register_for_season(self):
        response = self.client.post("/api/season/register/")
        self.assertEqual(response.status_code, 200)  # Response is 200 with message
        self.assertTrue(
            SeasonParticipant.objects.filter(
                season=self.season, profile=self.profile
            ).exists()
        )


class RankParticipantsTest(TestCase):
    def setUp(self):
        # Setup previous season
        self.prev_season = Season.objects.create(
            year=2025, month=12, status=Season.SeasonStatus.DONE
        )

        # 4 players in L1
        self.p1 = PlayerProfile.objects.create(profile_name="P1")
        self.p2 = PlayerProfile.objects.create(profile_name="P2")
        self.p3 = PlayerProfile.objects.create(profile_name="P3")
        self.p4 = PlayerProfile.objects.create(profile_name="P4")

        # 4 players in L2
        self.p5 = PlayerProfile.objects.create(profile_name="P5")
        self.p6 = PlayerProfile.objects.create(profile_name="P6")
        self.p7 = PlayerProfile.objects.create(profile_name="P7")
        self.p8 = PlayerProfile.objects.create(profile_name="P8")

        # Previous season participants
        self.prev_participants = {}
        for p in [
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            self.p5,
            self.p6,
            self.p7,
            self.p8,
        ]:
            self.prev_participants[p.profile_name] = SeasonParticipant.objects.create(
                season=self.prev_season, profile=p
            )

        self.l1 = League.objects.create(season=self.prev_season, level=1)
        self.l2 = League.objects.create(season=self.prev_season, level=2)

        # Add participants to leagues
        for p_name in ["P1", "P2", "P3", "P4"]:
            self.l1.members.add(self.prev_participants[p_name])
        for p_name in ["P5", "P6", "P7", "P8"]:
            self.l2.members.add(self.prev_participants[p_name])

        # L1 standings
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p1, league_points=10
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p2, league_points=8
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p3, league_points=6
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p4, league_points=4
        )  # Last in L1

        # L2 standings
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p5, league_points=10
        )  # Winner L2
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p6, league_points=8
        )
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p7, league_points=6
        )
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p8, league_points=4
        )

        # New season
        self.new_season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.OPEN
        )

        # Participants for new season: all old ones + some new ones
        self.new_p1 = PlayerProfile.objects.create(profile_name="New1")
        self.new_p2 = PlayerProfile.objects.create(profile_name="New2")

        self.all_profiles = [
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            self.p5,
            self.p6,
            self.p7,
            self.p8,
            self.new_p1,
            self.new_p2,
        ]
        self.participants = []
        for p in self.all_profiles:
            self.participants.append(
                SeasonParticipant.objects.create(season=self.new_season, profile=p)
            )

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
        self.assertEqual(ranked_profiles[3], self.p5)  # Promoted
        self.assertEqual(ranked_profiles[4], self.p4)  # Relegated
        self.assertEqual(ranked_profiles[5], self.p6)
        self.assertEqual(ranked_profiles[6], self.p7)
        self.assertEqual(ranked_profiles[7], self.p8)

        # New players should be at the end
        self.assertIn(ranked_profiles[8], [self.new_p1, self.new_p2])
        self.assertIn(ranked_profiles[9], [self.new_p1, self.new_p2])


def _row(name, league, position, is_last=False):
    return {
        "profile": name,
        "league": league,
        "position": position,
        "is_last": is_last,
    }


class ApplyPromotionRulesTest(TestCase):
    """Pure logic tests for apply_promotion covering the
    promotion-guaranteed and last-forces-relegation rules.
    """

    def test_classic_swap_when_full_league_sizes_match(self):
        # 8 players, sizes [4, 4]. Last of L1 swaps with winner of L2.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
            _row("G", 2, 3),
            _row("H", 2, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        self.assertEqual(result, ["A", "B", "C", "E", "D", "F", "G", "H"])

    def test_third_of_higher_league_relegated_to_keep_promotion(self):
        # New L1 shrinks to 3, L2 to 2. Winner of L2 must still be promoted
        # even though L1 is "full" without him; the 3rd of L1 is relegated.
        # Last of L1 (D) did not register.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("E", 2, 1),
            _row("F", 2, 2, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [3, 2])]
        # A, B keep L1; E promoted into L1; C relegated to L2; F stays last.
        self.assertEqual(result[:3], ["A", "B", "E"])
        self.assertEqual(set(result[3:]), {"C", "F"})
        # F was last in L2 -> should land in the bottom-most spot.
        self.assertEqual(result[-1], "F")

    def test_last_forces_relegation_pulling_extra_promotion_from_below(self):
        # Two L1 players did not register (A, B). D was last of L1 and
        # must still be relegated; F and G get promoted from L2 to fill L1.
        rows = [
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
            _row("G", 2, 3),
            _row("H", 2, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 2])]
        # New L1 = [C, E, F, G]; D forced down to L2 with H.
        self.assertEqual(result[:4], ["C", "E", "F", "G"])
        self.assertEqual(set(result[4:]), {"D", "H"})

    def test_collapsed_pyramid_promotion_outranks_relegation(self):
        # Previous 5 leagues x 4 players. All of L2, L3, L4 skip
        # registration. L1 and L5 register fully -> 8 players, new
        # structure [4, 4]. The winner of L5 (Q) must be promoted into
        # new L1, and the last of L1 (D) must be relegated to new L2.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("Q", 5, 1),
            _row("R", 5, 2),
            _row("S", 5, 3),
            _row("T", 5, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        self.assertEqual(set(result[:4]), {"A", "B", "C", "Q"})
        self.assertEqual(set(result[4:]), {"D", "R", "S", "T"})
        # Q (promoted winner) must end up above D (relegated last).
        self.assertLess(result.index("Q"), result.index("D"))

    def test_no_violation_when_winner_already_in_higher_league(self):
        # Standard case with new players: previous registered players
        # already line up correctly, no swap needed.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        # E promoted above D (the last), D relegated.
        self.assertEqual(result, ["A", "B", "C", "E", "D", "F"])
