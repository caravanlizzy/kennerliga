from django.test import TestCase
from rest_framework.test import APIClient

from user.models import User, PushDevice


class PushDeviceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="push-user", ******)
        self.client.force_authenticate(user=self.user)

    def test_register_push_device(self):
        response = self.client.post(
            "/api/user/me/push-devices/",
            {
                "token": "device-token-1",
                "platform": "android",
                "device_id": "android-1",
                "notify_registration_open": True,
                "notify_league_started": True,
                "notify_active_player": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            PushDevice.objects.filter(user=self.user, token="device-token-1").exists()
        )

    def test_register_existing_token_reassigns_owner(self):
        other = User.objects.create_user(username="other-user", ******)
        PushDevice.objects.create(user=other, token="shared-token", platform="ios")

        response = self.client.post(
            "/api/user/me/push-devices/",
            {"token": "shared-token", "platform": "ios"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        device = PushDevice.objects.get(token="shared-token")
        self.assertEqual(device.user_id, self.user.id)
        self.assertTrue(device.is_active)

    def test_list_and_deactivate_push_device(self):
        PushDevice.objects.create(
            user=self.user,
            token="to-remove",
            platform="android",
            is_active=True,
        )

        list_response = self.client.get("/api/user/me/push-devices/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

        delete_response = self.client.delete(
            "/api/user/me/push-devices/",
            {"token": "to-remove"},
            format="json",
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.data["deactivated"], 1)

        device = PushDevice.objects.get(token="to-remove")
        self.assertFalse(device.is_active)
