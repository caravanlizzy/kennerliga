from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform

class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = PlayerProfile.objects.create(user=self.user, profile_name='Test Profile')
        self.client.force_authenticate(user=self.user)

    def test_me_endpoint_no_league(self):
        response = self.client.get('/api/user/me/current-league/')
        self.assertEqual(response.status_code, 404)

    def test_get_profiles(self):
        response = self.client.get('/api/user/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
