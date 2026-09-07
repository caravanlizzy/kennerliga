from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from notification.models import PushSubscription
from user.models import User


class PushSubscriptionAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="password")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.subscription = {
            "endpoint": "https://push.example.test/subscription",
            "keys": {"p256dh": "public-key", "auth": "auth-key"},
        }

    @override_settings(VAPID_PUBLIC_KEY="test-public-key")
    def test_authenticated_user_can_register_a_push_subscription(self):
        response = self.client.get("/api/notifications/vapid-public-key/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"public_key": "test-public-key"})

        response = self.client.post(
            "/api/notifications/subscriptions/", self.subscription, format="json"
        )
        self.assertEqual(response.status_code, 204)
        registered = PushSubscription.objects.get()
        self.assertEqual(registered.user, self.user)
        self.assertEqual(registered.endpoint, self.subscription["endpoint"])

    def test_vapid_key_is_unavailable_without_configuration(self):
        response = self.client.get("/api/notifications/vapid-public-key/")
        self.assertEqual(response.status_code, 503)
