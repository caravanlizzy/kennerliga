from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from game.models import Game, SelectedGame
from league.models import League
from result.models import Result, EloChange
from season.models import Season, SeasonParticipant
from services.elo import (
    INITIAL_ELO,
    K_FACTOR,
    calculate_multiplayer_elo,
    expected_score,
    actual_score,
    apply_elo_for_selected_game,
    rebuild_all_elo,
    get_elo_rank,
)
from user.models import PlayerProfile, Platform

User = get_user_model()


class EloServiceTests(TestCase):
    def test_expected_score(self):
        # Equal ratings
        self.assertAlmostEqual(expected_score(1500, 1500), 0.5)
        # Higher rating expects higher win probability
        self.assertGreater(expected_score(1600, 1400), 0.7)
        self.assertLess(expected_score(1400, 1600), 0.3)
        self.assertAlmostEqual(
            expected_score(1600, 1400) + expected_score(1400, 1600), 1.0
        )

    def test_actual_score(self):
        # Position 1 beats Position 2
        self.assertEqual(actual_score(1, 2), 1.0)
        self.assertEqual(actual_score(2, 1), 0.0)
        # Tie
        self.assertEqual(actual_score(1, 1), 0.5)

    def test_2player_calculation(self):
        results = [
            {"player_profile_id": 1, "position": 1},
            {"player_profile_id": 2, "position": 2},
        ]
        current_ratings = {1: 1500.0, 2: 1500.0}
        new_ratings, deltas = calculate_multiplayer_elo(results, current_ratings)

        # In 2p equal rating match with K=32:
        # Expected = 0.5, Actual for winner = 1.0 -> Delta = 32 * (1.0 - 0.5) = +16
        self.assertAlmostEqual(deltas[1], 16.0)
        self.assertAlmostEqual(deltas[2], -16.0)
        self.assertAlmostEqual(new_ratings[1], 1516.0)
        self.assertAlmostEqual(new_ratings[2], 1484.0)

    def test_4player_calculation(self):
        results = [
            {"player_profile_id": 1, "position": 1},
            {"player_profile_id": 2, "position": 2},
            {"player_profile_id": 3, "position": 3},
            {"player_profile_id": 4, "position": 4},
        ]
        current_ratings = {1: 1500.0, 2: 1500.0, 3: 1500.0, 4: 1500.0}
        new_ratings, deltas = calculate_multiplayer_elo(results, current_ratings)

        # Player 1 beats 3 players: deltas sum = 16 + 16 + 16 = 48. Average over 3 opponents = +16
        self.assertAlmostEqual(deltas[1], 16.0)
        # Player 4 loses to 3 players: average = -16
        self.assertAlmostEqual(deltas[4], -16.0)
        # Player 2 loses to 1, beats 2 and 3: (-16 + 16 + 16) / 3 = 16/3 = +5.333
        self.assertAlmostEqual(deltas[2], 16.0 / 3.0)
        # Player 3 loses to 1 and 2, beats 4: (-16 - 16 + 16) / 3 = -16/3 = -5.333
        self.assertAlmostEqual(deltas[3], -16.0 / 3.0)

        # Sum of deltas in symmetric ratings match must be 0
        self.assertAlmostEqual(sum(deltas.values()), 0.0)

    def test_multiplayer_tie(self):
        results = [
            {"player_profile_id": 1, "position": 1},
            {"player_profile_id": 2, "position": 1},
            {"player_profile_id": 3, "position": 3},
        ]
        current_ratings = {1: 1500.0, 2: 1500.0, 3: 1500.0}
        new_ratings, deltas = calculate_multiplayer_elo(results, current_ratings)

        # Player 1 draws with Player 2 (0 delta) and beats Player 3 (+16 delta) -> average delta = +8
        self.assertAlmostEqual(deltas[1], 8.0)
        self.assertAlmostEqual(deltas[2], 8.0)
        # Player 3 loses to Player 1 (-16) and Player 2 (-16) -> average delta = -16
        self.assertAlmostEqual(deltas[3], -16.0)


class EloIntegrationTests(TestCase):
    def setUp(self):
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )
        self.league = League.objects.create(season=self.season, level=1)
        self.platform = Platform.objects.create(name="BGA")
        self.game = Game.objects.create(name="Terraforming Mars", platform=self.platform)

        self.users = []
        self.profiles = []
        for i in range(1, 5):
            u = User.objects.create_user(username=f"player{i}", password="password")
            p = PlayerProfile.objects.create(
                user=u, profile_name=f"Player {i}", elo_rating=1500.0
            )
            SeasonParticipant.objects.create(season=self.season, profile=p)
            self.league.members.add(SeasonParticipant.objects.get(season=self.season, profile=p))
            self.users.append(u)
            self.profiles.append(p)

        self.selected_game = SelectedGame.objects.create(
            game=self.game, league=self.league, profile=self.profiles[0]
        )

    def test_apply_elo_for_selected_game(self):
        # Create results
        for idx, p in enumerate(self.profiles, start=1):
            Result.objects.create(
                player_profile=p,
                selected_game=self.selected_game,
                league=self.league,
                season=self.season,
                position=idx,
                points=100 - idx * 10,
            )

        changes = apply_elo_for_selected_game(self.selected_game)
        self.assertEqual(len(changes), 4)

        # Verify profiles updated
        self.profiles[0].refresh_from_db()
        self.profiles[3].refresh_from_db()
        self.assertAlmostEqual(self.profiles[0].elo_rating, 1516.0)
        self.assertAlmostEqual(self.profiles[3].elo_rating, 1484.0)

        # Verify EloChange records created
        self.assertEqual(
            EloChange.objects.filter(selected_game=self.selected_game).count(), 4
        )

        # Check ranks
        rank1 = get_elo_rank(self.profiles[0])
        rank4 = get_elo_rank(self.profiles[3])
        self.assertEqual(rank1, 1)
        self.assertEqual(rank4, 4)

    def test_rebuild_all_elo(self):
        # Create match 1
        for idx, p in enumerate(self.profiles, start=1):
            Result.objects.create(
                player_profile=p,
                selected_game=self.selected_game,
                league=self.league,
                season=self.season,
                position=idx,
                points=100 - idx * 10,
            )

        # Tamper profile rating
        self.profiles[0].elo_rating = 2000.0
        self.profiles[0].save()

        count = rebuild_all_elo()
        self.assertEqual(count, 1)

        self.profiles[0].refresh_from_db()
        self.assertAlmostEqual(self.profiles[0].elo_rating, 1516.0)

    def test_user_statistics_includes_elo(self):
        # Apply match
        for idx, p in enumerate(self.profiles, start=1):
            Result.objects.create(
                player_profile=p,
                selected_game=self.selected_game,
                league=self.league,
                season=self.season,
                position=idx,
                points=100 - idx * 10,
            )
        apply_elo_for_selected_game(self.selected_game)

        token = Token.objects.create(user=self.users[0])
        response = self.client.get(
            f"/api/user/users/{self.users[0].id}/statistics/",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("elo", data)
        self.assertAlmostEqual(data["elo"]["rating"], 1516.0)
        self.assertEqual(data["elo"]["rank"], 1)
        self.assertTrue(len(data["elo"]["history"]) > 0)
