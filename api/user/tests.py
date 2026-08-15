from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile
from season.models import Season, SeasonParticipant


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
