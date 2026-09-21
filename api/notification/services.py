import json
import logging
import os

from django.conf import settings
from django.db import transaction
from pywebpush import WebPushException, webpush

from notification.models import PushSubscription

logger = logging.getLogger(__name__)


def _web_push_is_configured():
    return bool(
        settings.VAPID_PRIVATE_KEY
        and settings.VAPID_PUBLIC_KEY
        and settings.VAPID_SUBJECT
    )


def _missing_vapid_settings():
    """
    Returns the names of the VAPID settings that are unset, so a
    misconfiguration can be logged by name without ever logging the key
    material itself.
    """
    missing = []
    if not settings.VAPID_PUBLIC_KEY:
        missing.append("VAPID_PUBLIC_KEY")
    if not settings.VAPID_PRIVATE_KEY:
        missing.append("VAPID_PRIVATE_KEY")
    if not settings.VAPID_SUBJECT:
        missing.append("VAPID_SUBJECT")
    return missing


def notify_users(user_ids, title, body, url="/"):
    user_ids = list(set(user_ids))
    if not user_ids:
        return
    if not _web_push_is_configured():
        logger.warning(
            "Push notification skipped: VAPID not configured (missing %s).",
            ", ".join(_missing_vapid_settings()),
        )
        return
    transaction.on_commit(
        lambda: _send_to_users(user_ids, {"title": title, "body": body, "url": url})
    )


def notify_all_users(title, body, url="/"):
    if not _web_push_is_configured():
        logger.warning(
            "Push notification skipped: VAPID not configured (missing %s).",
            ", ".join(_missing_vapid_settings()),
        )
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
        "/#/my",
    )


def _send_to_users(user_ids, payload):
    """
    Sends `payload` to every push subscription owned by `user_ids` and
    returns `(targeted, succeeded)`. Stale subscriptions (404/410) are
    pruned. A VAPID key that cannot be parsed is logged once as an
    actionable error rather than repeated for every subscription.
    """
    subscriptions = list(PushSubscription.objects.filter(user_id__in=user_ids))
    targeted = len(subscriptions)
    succeeded = 0
    private_key = _normalize_private_key(settings.VAPID_PRIVATE_KEY)

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=json.dumps(payload),
                vapid_private_key=private_key,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
            succeeded += 1
        except WebPushException as error:
            response = error.response
            if response is not None and response.status_code in (404, 410):
                subscription.delete()
            else:
                logger.exception(
                    "Unable to send push notification to subscription %s", subscription.id
                )
        except (ValueError, TypeError):
            # A malformed VAPID private key fails identically for every
            # subscription, so report it once and stop rather than logging
            # the same parse error per subscription. The key itself is
            # never logged.
            logger.error(
                "VAPID key invalid: the configured VAPID_PRIVATE_KEY could not "
                "be parsed; aborting push send after %s of %s subscription(s).",
                succeeded,
                targeted,
            )
            break

    return targeted, succeeded


def _normalize_private_key(raw):
    """
    Prepares a configured VAPID private key for `pywebpush`. A PEM pasted
    into a `.env` file is often wrapped in quotes and has its newlines
    escaped as literal ``\\n``; both are undone here so the key parses.

    A value that is a path to an existing key file (pywebpush's other
    supported form) is returned untouched.
    """
    if not raw:
        return raw

    value = raw.strip()
    if value and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    if os.path.isfile(value):
        return value
    return value.replace("\\n", "\n")


def send_test_notification(user):
    """
    Sends a notification to the requesting user's own subscriptions so the
    end-to-end pipeline can be exercised on demand. Returns a dict with
    whether VAPID is configured and how many subscriptions were targeted
    and succeeded.
    """
    if not _web_push_is_configured():
        logger.warning(
            "Test push notification skipped: VAPID not configured (missing %s).",
            ", ".join(_missing_vapid_settings()),
        )
        return {"configured": False, "targeted": 0, "succeeded": 0}

    targeted, succeeded = _send_to_users(
        [user.id],
        {
            "title": "Kennerliga test notification",
            "body": "Push notifications are working.",
            "url": "/",
        },
    )
    return {"configured": True, "targeted": targeted, "succeeded": succeeded}
