from unittest import mock

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from notification import services
from notification.models import PushSubscription
from user.models import User

VAPID_SETTINGS = {
    "VAPID_PUBLIC_KEY": "test-public-key",
    "VAPID_PRIVATE_KEY": "test-private-key",
    "VAPID_SUBJECT": "mailto:admin@example.test",
}


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


class TestSendNotificationEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="password")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_test_endpoint_returns_503_when_unconfigured(self):
        response = self.client.post("/api/notifications/test/")
        self.assertEqual(response.status_code, 503)

    @override_settings(**VAPID_SETTINGS)
    def test_test_endpoint_reports_targeted_and_succeeded_counts(self):
        PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.test/a",
            p256dh="p256dh",
            auth="auth",
        )
        with mock.patch("notification.services.webpush") as webpush:
            response = self.client.post("/api/notifications/test/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"targeted": 1, "succeeded": 1})
        webpush.assert_called_once()


class NotifyUsersConfigurationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="password")

    def test_notify_users_logs_warning_and_sends_nothing_when_unset(self):
        with override_settings(
            VAPID_PUBLIC_KEY="", VAPID_PRIVATE_KEY="", VAPID_SUBJECT=""
        ):
            with self.assertLogs("notification.services", level="WARNING") as logs:
                services.notify_users([self.user.id], "Title", "Body")
        self.assertTrue(
            any("VAPID_PUBLIC_KEY" in message for message in logs.output)
        )


class NormalizePrivateKeyTests(TestCase):
    def test_escaped_newlines_and_quotes_are_restored(self):
        raw = '"-----BEGIN PRIVATE KEY-----\\nABC\\n-----END PRIVATE KEY-----"'
        normalized = services._normalize_private_key(raw)
        self.assertEqual(
            normalized,
            "-----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----",
        )

    def test_empty_value_is_returned_unchanged(self):
        self.assertEqual(services._normalize_private_key(""), "")


class SendToUsersPruningTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="password")
        self.subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.test/gone",
            p256dh="p256dh",
            auth="auth",
        )

    @override_settings(**VAPID_SETTINGS)
    def test_expired_subscription_is_pruned_and_not_counted(self):
        response = mock.Mock(status_code=410)
        error = services_webpush_exception(response)
        with mock.patch("notification.services.webpush", side_effect=error):
            targeted, succeeded = services._send_to_users(
                [self.user.id], {"title": "t", "body": "b", "url": "/"}
            )
        self.assertEqual((targeted, succeeded), (1, 0))
        self.assertFalse(PushSubscription.objects.filter(id=self.subscription.id).exists())

    @override_settings(**VAPID_SETTINGS)
    def test_malformed_key_is_logged_once(self):
        with mock.patch("notification.services.webpush", side_effect=ValueError("bad key")):
            with self.assertLogs("notification.services", level="ERROR") as logs:
                targeted, succeeded = services._send_to_users(
                    [self.user.id], {"title": "t", "body": "b", "url": "/"}
                )
        self.assertEqual((targeted, succeeded), (1, 0))
        self.assertEqual(
            sum("VAPID key invalid" in message for message in logs.output), 1
        )


def services_webpush_exception(response):
    from pywebpush import WebPushException

    error = WebPushException("gone")
    error.response = response
    return error


class NotifyTurnTests(TestCase):
    def setUp(self):
        from league.models import League, LeagueStatus
        from season.models import Season, SeasonParticipant
        from user.models import PlayerProfile

        self.user = User.objects.create_user(username="player", password="password")
        self.profile = PlayerProfile.objects.create(user=self.user, profile_name="player")
        self.season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        self.participant = SeasonParticipant.objects.create(season=self.season, profile=self.profile)
        self.league = League.objects.create(season=self.season, level=1, status=LeagueStatus.PICKING)
        self.league.members.add(self.participant)
        self.league.active_player = self.participant
        self.league.save()

    def test_notify_turn_when_active_and_picking(self):
        with mock.patch("notification.services.notify_users") as mock_notify:
            services.notify_turn(self.league, self.participant)
            mock_notify.assert_called_once_with(
                [self.user.id],
                "Your turn in Kennerliga",
                f"It is your turn in {self.league}.",
                "/#/my",
            )

    def test_no_notify_turn_when_league_playing_or_done(self):
        from league.models import LeagueStatus

        for status in (LeagueStatus.PLAYING, LeagueStatus.DONE):
            self.league.status = status
            self.league.save()
            with mock.patch("notification.services.notify_users") as mock_notify:
                services.notify_turn(self.league, self.participant)
                mock_notify.assert_not_called()

    def test_no_notify_turn_when_season_not_running(self):
        from season.models import Season

        self.season.status = Season.SeasonStatus.DONE
        self.season.save()
        with mock.patch("notification.services.notify_users") as mock_notify:
            services.notify_turn(self.league, self.participant)
            mock_notify.assert_not_called()

    def test_no_notify_turn_when_not_active_player(self):
        from season.models import SeasonParticipant
        from user.models import PlayerProfile

        other_user = User.objects.create_user(username="other", password="password")
        other_profile = PlayerProfile.objects.create(user=other_user, profile_name="other")
        other_participant = SeasonParticipant.objects.create(season=self.season, profile=other_profile)

        with mock.patch("notification.services.notify_users") as mock_notify:
            services.notify_turn(self.league, other_participant)
            mock_notify.assert_not_called()
