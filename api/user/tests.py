from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import Game, SelectedGame
from result.models import Result
from user.service import get_user_summary_stats
from user.serializers import UserSerializer


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = PlayerProfile.objects.create(
            user=self.user, profile_name="Test Profile"
        )
        self.client.force_authenticate(user=self.user)

    def test_me_endpoint_no_league(self):
        response = self.client.get("/api/user/me/current-league/")
        self.assertEqual(response.status_code, 404)

    def test_get_profiles(self):
        response = self.client.get("/api/user/profiles/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_user_by_exact_username_case_insensitive(self):
        # By ID
        res_id = self.client.get(f"/api/user/users/{self.user.id}/")
        self.assertEqual(res_id.status_code, 200)
        self.assertEqual(res_id.data["username"], "testuser")

        # By exact username
        res_name = self.client.get("/api/user/users/testuser/")
        self.assertEqual(res_name.status_code, 200)
        self.assertEqual(res_name.data["id"], self.user.id)

        # By case-insensitive username
        res_case = self.client.get("/api/user/users/TestUser/")
        self.assertEqual(res_case.status_code, 200)
        self.assertEqual(res_case.data["id"], self.user.id)

        # Query param
        res_query = self.client.get("/api/user/users/?username=TESTUSER")
        self.assertEqual(res_query.status_code, 200)
        self.assertEqual(len(res_query.data), 1)
        self.assertEqual(res_query.data[0]["id"], self.user.id)

    def test_season_participants_sorted_with_season_details(self):
        s1 = Season.objects.create(year=2025, month=11)
        s2 = Season.objects.create(year=2025, month=12)
        s3 = Season.objects.create(year=2026, month=1)

        p1 = SeasonParticipant.objects.create(season=s1, profile=self.profile)
        p2 = SeasonParticipant.objects.create(season=s2, profile=self.profile)
        p3 = SeasonParticipant.objects.create(season=s3, profile=self.profile)

        response = self.client.get(f"/api/season/season-participants/?profile={self.profile.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # Verify sorted latest first
        self.assertEqual(response.data[0]["id"], p3.id)
        self.assertEqual(response.data[1]["id"], p2.id)
        self.assertEqual(response.data[2]["id"], p1.id)

        # Verify season_details is included
        self.assertIn("season_details", response.data[0])
        self.assertEqual(response.data[0]["season_details"]["year"], 2026)
        self.assertEqual(response.data[0]["season_details"]["month"], 1)

    def test_user_summary_stats_empty(self):
        stats = get_user_summary_stats(self.user)
        self.assertIsNone(stats["win_rate"])
        self.assertIsNone(stats["avg_position"])
        self.assertIsNone(stats["most_participated_league_level"])

        serializer = UserSerializer(self.user)
        self.assertIsNone(serializer.data["win_rate"])
        self.assertIsNone(serializer.data["avg_position"])
        self.assertIsNone(serializer.data["most_participated_league_level"])

    def test_user_summary_stats_calculations(self):
        platform = Platform.objects.create(name="BGA_test")
        season1 = Season.objects.create(year=2026, month=1)
        season2 = Season.objects.create(year=2026, month=2)
        season3 = Season.objects.create(year=2026, month=3)

        part1 = SeasonParticipant.objects.create(season=season1, profile=self.profile)
        part2 = SeasonParticipant.objects.create(season=season2, profile=self.profile)
        part3 = SeasonParticipant.objects.create(season=season3, profile=self.profile)

        # 2 leagues at level 2, 1 league at level 1
        l1 = League.objects.create(season=season1, level=2, status=LeagueStatus.PLAYING)
        l1.members.add(part1)

        l2 = League.objects.create(season=season2, level=2, status=LeagueStatus.PLAYING)
        l2.members.add(part2)

        l3 = League.objects.create(season=season3, level=1, status=LeagueStatus.PLAYING)
        l3.members.add(part3)

        game = Game.objects.create(name="Terraforming Mars", platform=platform)
        sg1 = SelectedGame.objects.create(game=game, league=l1, profile=self.profile)
        sg2 = SelectedGame.objects.create(game=game, league=l2, profile=self.profile)
        sg3 = SelectedGame.objects.create(game=game, league=l3, profile=self.profile)

        # Positions: 1, 2, 3 -> wins = 1/3 (33.3%), avg_position = (1+2+3)/3 = 2.0
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg1,
            season=season1,
            league=l1,
            position=1,
            points=100,
        )
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg2,
            season=season2,
            league=l2,
            position=2,
            points=90,
        )
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg3,
            season=season3,
            league=l3,
            position=3,
            points=80,
        )

        stats = get_user_summary_stats(self.user)
        self.assertEqual(stats["win_rate"], 33.3)
        self.assertEqual(stats["avg_position"], 2.0)
        self.assertEqual(stats["most_participated_league_level"], 2)

        res = self.client.get(f"/api/user/users/{self.user.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["win_rate"], 33.3)
        self.assertEqual(res.data["avg_position"], 2.0)
        self.assertEqual(res.data["most_participated_league_level"], 2)

    def test_user_summary_stats_tie_breaking_league_level(self):
        season1 = Season.objects.create(year=2026, month=1)
        season2 = Season.objects.create(year=2026, month=2)

        part1 = SeasonParticipant.objects.create(season=season1, profile=self.profile)
        part2 = SeasonParticipant.objects.create(season=season2, profile=self.profile)

        l1 = League.objects.create(season=season1, level=2)
        l1.members.add(part1)

        l2 = League.objects.create(season=season2, level=1)
        l2.members.add(part2)

        stats = get_user_summary_stats(self.user)
        # When tie between level 1 and 2 (both 1 participation), level 1 wins (lowest level number)
        self.assertEqual(stats["most_participated_league_level"], 1)

    def test_user_without_profile(self):
        user_no_prof = User.objects.create_user(username="noprof", password="password")
        stats = get_user_summary_stats(user_no_prof)
        self.assertIsNone(stats["win_rate"])
        self.assertIsNone(stats["avg_position"])
        self.assertIsNone(stats["most_participated_league_level"])

        serializer = UserSerializer(user_no_prof)
        self.assertIsNone(serializer.data["win_rate"])
        self.assertIsNone(serializer.data["avg_position"])
        self.assertIsNone(serializer.data["most_participated_league_level"])

    def test_user_summary_stats_exclude_2p_and_3p_games(self):
        platform = Platform.objects.create(name="BGA_filter_test")
        season = Season.objects.create(year=2026, month=1)
        part = SeasonParticipant.objects.create(season=season, profile=self.profile)
        league = League.objects.create(season=season, level=1, status=LeagueStatus.PLAYING)
        league.members.add(part)

        game_2p = Game.objects.create(
            name="Patchwork", min_players=2, max_players=2, platform=platform
        )
        game_3p = Game.objects.create(
            name="Maria", min_players=3, max_players=3, platform=platform
        )
        game_4p = Game.objects.create(
            name="Terraforming Mars", min_players=2, max_players=4, platform=platform
        )

        sg_2p = SelectedGame.objects.create(game=game_2p, league=league, profile=self.profile)
        sg_3p = SelectedGame.objects.create(game=game_3p, league=league, profile=self.profile)
        sg_4p = SelectedGame.objects.create(game=game_4p, league=league, profile=self.profile)

        # 2p: pos 1, 3p: pos 2, 4p: pos 3
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg_2p,
            season=season,
            league=league,
            position=1,
            points=100,
        )
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg_3p,
            season=season,
            league=league,
            position=2,
            points=90,
        )
        Result.objects.create(
            player_profile=self.profile,
            selected_game=sg_4p,
            season=season,
            league=league,
            position=3,
            points=80,
        )

        # Base: all 3 games -> 1 win, avg 2.0
        stats_all = get_user_summary_stats(self.user)
        self.assertEqual(stats_all["win_rate"], 33.3)
        self.assertEqual(stats_all["avg_position"], 2.0)

        # Exclude 2p: games 3p & 4p -> 0 wins, avg (2+3)/2 = 2.5
        stats_no_2p = get_user_summary_stats(self.user, exclude_2p_only=True)
        self.assertEqual(stats_no_2p["win_rate"], 0.0)
        self.assertEqual(stats_no_2p["avg_position"], 2.5)

        # Exclude 3p: games 2p & 4p -> 1 win, avg (1+3)/2 = 2.0
        stats_no_3p = get_user_summary_stats(self.user, exclude_3p_only=True)
        self.assertEqual(stats_no_3p["win_rate"], 50.0)
        self.assertEqual(stats_no_3p["avg_position"], 2.0)

        # Exclude both 2p & 3p: game 4p only -> 0 wins, avg 3.0
        stats_no_2p_3p = get_user_summary_stats(
            self.user, exclude_2p_only=True, exclude_3p_only=True
        )
        self.assertEqual(stats_no_2p_3p["win_rate"], 0.0)
        self.assertEqual(stats_no_2p_3p["avg_position"], 3.0)

        # Test via list API endpoint with query params
        res_list_no_2p = self.client.get("/api/user/users/?exclude_2p_only=true")
        self.assertEqual(res_list_no_2p.status_code, 200)
        user_data = next(u for u in res_list_no_2p.data if u["id"] == self.user.id)
        self.assertEqual(user_data["win_rate"], 0.0)
        self.assertEqual(user_data["avg_position"], 2.5)

        res_list_no_3p = self.client.get("/api/user/users/?exclude_3p_only=true")
        self.assertEqual(res_list_no_3p.status_code, 200)
        user_data = next(u for u in res_list_no_3p.data if u["id"] == self.user.id)
        self.assertEqual(user_data["win_rate"], 50.0)
        self.assertEqual(user_data["avg_position"], 2.0)

        res_list_no_both = self.client.get(
            "/api/user/users/?exclude_2p_only=true&exclude_3p_only=true"
        )
        self.assertEqual(res_list_no_both.status_code, 200)
        user_data = next(u for u in res_list_no_both.data if u["id"] == self.user.id)
        self.assertEqual(user_data["win_rate"], 0.0)
        self.assertEqual(user_data["avg_position"], 3.0)

        # Test user statistics action endpoint
        res_stats_no_2p = self.client.get(
            f"/api/user/users/{self.user.id}/statistics/?exclude_2p_only=true"
        )
        self.assertEqual(res_stats_no_2p.status_code, 200)
        self.assertEqual(res_stats_no_2p.data["overall_stats"]["total_games"], 2)
        self.assertEqual(res_stats_no_2p.data["overall_stats"]["wins"], 0)
        self.assertEqual(res_stats_no_2p.data["overall_stats"]["avg_pos"], 2.5)
