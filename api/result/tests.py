from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import (
    Game,
    SelectedGame,
    ResultConfig,
    WinCondition,
    TieBreaker,
    StartingPointSystem,
)
from result.models import Result


class ResultAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_authenticate(user=self.user)

        self.platform = Platform.objects.create(name="BGA")
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user, profile_name="Admin Profile"
        )
        self.participant = SeasonParticipant.objects.create(
            season=self.season, profile=self.profile, rank=1
        )

        self.league = League.objects.create(
            season=self.season, level=1, status=LeagueStatus.PLAYING
        )
        self.league.members.add(self.participant)
        self.league.save()

        self.sps = StartingPointSystem.objects.create(
            id=1, code="FIXED", description="Fixed points"
        )
        self.game = Game.objects.create(
            name="Catan", min_players=1, max_players=4, platform=self.platform
        )
        self.config = ResultConfig.objects.create(
            game=self.game, has_points=True, starting_points_system=self.sps
        )
        self.win_condition = WinCondition.objects.create(
            result_config=self.config,
            name="Punkte",
            condition_type=WinCondition.WinConditionType.POINTS,
            order=0,
        )
        self.selected_game = SelectedGame.objects.create(
            game=self.game, league=self.league, profile=self.profile
        )

    def test_submit_match_result(self):
        # Create another player as MatchResultViewSet requires at least 2 results
        user2 = User.objects.create(username="user2")
        profile2 = PlayerProfile.objects.create(user=user2, profile_name="Profile 2")
        participant2 = SeasonParticipant.objects.create(
            season=self.season, profile=profile2, rank=2
        )
        self.league.members.add(participant2)

        data = {
            "selected_game": self.selected_game.id,
            "win_condition": self.win_condition.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1,
                },
                {"player_profile": profile2.id, "points": 8, "starting_position": 2},
            ],
        }
        response = self.client.post("/api/result/match-results/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Result.objects.count(), 2)

        result = Result.objects.get(player_profile=self.profile)
        self.assertEqual(result.points, 10)
        self.assertEqual(result.position, 1)

    def test_submit_match_result_with_tie(self):
        # Create another player
        user2 = User.objects.create(username="user2")
        profile2 = PlayerProfile.objects.create(user=user2, profile_name="Profile 2")
        participant2 = SeasonParticipant.objects.create(
            season=self.season, profile=profile2, rank=2
        )
        self.league.members.add(participant2)

        tb = TieBreaker.objects.create(win_condition=self.win_condition, name="TB1", order=1)

        data = {
            "selected_game": self.selected_game.id,
            "win_condition": self.win_condition.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1,
                },
                {"player_profile": profile2.id, "points": 10, "starting_position": 2},
            ],
        }
        # First submission with equal points
        response = self.client.post("/api/result/match-results/", data, format="json")
        # Based on result/views.py:152, it returns 202 ACCEPTED for ties
        self.assertEqual(response.status_code, 202)
        self.assertIn("tie_groups", response.data)

        # Submit with tiebreaker
        data["tiebreaker"] = {"id": tb.id}
        data["results"][0]["tie_breaker_value"] = 5
        data["results"][1]["tie_breaker_value"] = 3

        response = self.client.post("/api/result/match-results/", data, format="json")
        self.assertEqual(response.status_code, 201)

        res1 = Result.objects.get(player_profile=self.profile)
        res2 = Result.objects.get(player_profile=profile2)

        self.assertEqual(res1.position, 1)
        self.assertEqual(res2.position, 2)
        self.assertEqual(res1.decisive_tie_breaker, tb)

    def test_fractional_wins_on_tie(self):
        # Create another player
        user2 = User.objects.create(username="user2")
        profile2 = PlayerProfile.objects.create(user=user2, profile_name="Profile 2")
        participant2 = SeasonParticipant.objects.create(
            season=self.season, profile=profile2, rank=2
        )
        self.league.members.add(participant2)

        data = {
            "selected_game": self.selected_game.id,
            "win_condition": self.win_condition.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": 10,
                    "starting_position": 1,
                },
                {"player_profile": profile2.id, "points": 10, "starting_position": 2},
            ],
        }
        # Submission with equal points and NO tie-breakers defined for this game in setUp
        # Actually, let's make sure no tie-breakers exist so it stays a tie.
        TieBreaker.objects.filter(win_condition=self.win_condition).delete()

        response = self.client.post("/api/result/match-results/", data, format="json")
        # Since there are no tie-breakers, it should finalize immediately with a tie
        self.assertEqual(response.status_code, 201)

        from league.models import LeagueStanding, GameStanding

        # Check GameStanding for win_share
        gs1 = GameStanding.objects.get(
            selected_game=self.selected_game, player_profile=self.profile
        )
        gs2 = GameStanding.objects.get(
            selected_game=self.selected_game, player_profile=profile2
        )

        # Both should have 0.5 wins
        self.assertEqual(float(gs1.win_share), 0.5)
        self.assertEqual(float(gs2.win_share), 0.5)

        # Check LeagueStanding for total wins
        ls1 = LeagueStanding.objects.get(
            league=self.league, player_profile=self.profile
        )
        ls2 = LeagueStanding.objects.get(league=self.league, player_profile=profile2)

        self.assertEqual(float(ls1.wins), 0.5)
        self.assertEqual(float(ls2.wins), 0.5)

    def test_game_records_detection_and_user_profile(self):
        user2 = User.objects.create(username="user2")
        profile2 = PlayerProfile.objects.create(user=user2, profile_name="Profile 2")
        participant2 = SeasonParticipant.objects.create(
            season=self.season, profile=profile2, rank=2
        )
        self.league.members.add(participant2)

        # Game with points: profile scores 10 (record), profile2 scores 8
        r1 = Result.objects.create(
            selected_game=self.selected_game,
            player_profile=self.profile,
            points=10,
            position=1,
            league=self.league,
            season=self.season,
        )
        r2 = Result.objects.create(
            selected_game=self.selected_game,
            player_profile=profile2,
            points=8,
            position=2,
            league=self.league,
            season=self.season,
        )

        # Test queries
        from result.queries import get_game_records_map
        records = get_game_records_map()
        self.assertEqual(records.get(self.game.id), 10)

        # Test ResultSerializer
        from result.serializers import ResultSerializer
        s1 = ResultSerializer(r1).data
        s2 = ResultSerializer(r2).data
        self.assertTrue(s1["is_record"])
        self.assertFalse(s2["is_record"])

        # Test a 1-point score is not considered a record (min 2 points)
        game2 = Game.objects.create(name="GameNoPoints", min_players=1, max_players=4, platform=self.platform)
        ResultConfig.objects.create(game=game2, has_points=False)
        sg2 = SelectedGame.objects.create(game=game2, league=self.league, profile=self.profile)
        r3 = Result.objects.create(
            selected_game=sg2,
            player_profile=self.profile,
            points=1,
            position=1,
            league=self.league,
            season=self.season,
        )
        records_after = get_game_records_map()
        self.assertNotIn(game2.id, records_after)
        self.assertFalse(ResultSerializer(r3).data["is_record"])

        # Test user statistics returns held records
        stats_resp = self.client.get(f"/api/user/users/{self.user.id}/statistics/")
        self.assertEqual(stats_resp.status_code, 200)
        self.assertIn("records", stats_resp.data)
        held_records = stats_resp.data["records"]
        self.assertEqual(len(held_records), 1)
        self.assertEqual(held_records[0]["game_id"], self.game.id)
        self.assertEqual(held_records[0]["game_name"], "Catan")
        self.assertEqual(held_records[0]["record_score"], 10)

        # User 2 shouldn't have any records
        stats_resp2 = self.client.get(f"/api/user/users/{user2.id}/statistics/")
        self.assertEqual(stats_resp2.status_code, 200)
        self.assertEqual(len(stats_resp2.data["records"]), 0)

    def test_submit_match_result_with_decimal_points(self):
        user2 = User.objects.create(username="user2")
        profile2 = PlayerProfile.objects.create(user=user2, profile_name="Profile 2")
        participant2 = SeasonParticipant.objects.create(
            season=self.season, profile=profile2, rank=2
        )
        self.league.members.add(participant2)

        data = {
            "selected_game": self.selected_game.id,
            "win_condition": self.win_condition.id,
            "results": [
                {
                    "player_profile": self.profile.id,
                    "points": -0.5,
                    "starting_position": 1,
                    "starting_points": -0.5,
                },
                {
                    "player_profile": profile2.id,
                    "points": -1.0,
                    "starting_position": 2,
                    "starting_points": 0,
                },
            ],
        }
        response = self.client.post("/api/result/match-results/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Result.objects.count(), 2)

        res1 = Result.objects.get(player_profile=self.profile)
        res2 = Result.objects.get(player_profile=profile2)

        self.assertEqual(float(res1.points), -0.5)
        self.assertEqual(float(res1.starting_points), -0.5)
        self.assertEqual(res1.position, 1)

        self.assertEqual(float(res2.points), -1.0)
        self.assertEqual(float(res2.starting_points), 0.0)
        self.assertEqual(res2.position, 2)

        # Verify ResultSerializer serialization formats numbers without trailing .00 strings
        from result.serializers import ResultSerializer
        r_neg8 = Result.objects.create(
            selected_game=self.selected_game,
            player_profile=self.profile,
            points=-8,
            starting_points=-0.5,
            position=1,
            league=self.league,
            season=self.season,
        )
        s_data = ResultSerializer(r_neg8).data
        from rest_framework.renderers import JSONRenderer
        import json
        rendered = json.loads(JSONRenderer().render(s_data))
        self.assertEqual(rendered["points"], -8.0)
        self.assertEqual(rendered["starting_points"], -0.5)
