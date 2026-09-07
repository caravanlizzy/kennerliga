import json
import logging

from django.conf import settings
from django.db import transaction

from notification.models import PushSubscription

logger = logging.getLogger(__name__)


def _web_push_is_configured():
    return bool(
        settings.VAPID_PRIVATE_KEY
        and settings.VAPID_PUBLIC_KEY
        and settings.VAPID_SUBJECT
    )


def notify_users(user_ids, title, body, url="/"):
    user_ids = list(set(user_ids))
    if not user_ids or not _web_push_is_configured():
        return
    transaction.on_commit(
        lambda: _send_to_users(user_ids, {"title": title, "body": body, "url": url})
    )


def notify_all_users(title, body, url="/"):
    if not _web_push_is_configured():
        return
    transaction.on_commit(
        lambda: _send_to_users(
            list(PushSubscription.objects.values_list("user_id", flat=True).distinct()),
            {"title": title, "body": body, "url": url},
        )
    )


def notify_turn(league, participant):
    user_id = participant.profile.user_id
    if user_id is None:
        return
    notify_users(
        [user_id],
        "Your turn in Kennerliga",
        f"It is your turn in {league}.",
        "/#/league/my-league",
    )


def _send_to_users(user_ids, payload):
    from pywebpush import WebPushException, webpush

    subscriptions = PushSubscription.objects.filter(user_id__in=user_ids)
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
        except WebPushException as error:
            response = error.response
            if response is not None and response.status_code in (404, 410):
                subscription.delete()
            else:
                logger.exception("Unable to send push notification to subscription %s", subscription.id)
