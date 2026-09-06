import json
import logging
import os
from typing import Optional, Iterable

from django.conf import settings
from django.db import transaction

from user.models import PushDevice

logger = logging.getLogger(__name__)


def _split_chunks(values: list[str], size: int = 500) -> Iterable[list[str]]:
    for i in range(0, len(values), size):
        yield values[i : i + size]


def _load_firebase_credential():
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        from firebase_admin import credentials

        return credentials.Certificate(json.loads(service_account_json))

    service_account_file = os.environ.get("FIREBASE_SERVICE_ACCOUNT_FILE")
    if service_account_file:
        from firebase_admin import credentials

        return credentials.Certificate(service_account_file)

    configured = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_FILE", None)
    if configured:
        from firebase_admin import credentials

        return credentials.Certificate(configured)

    return None


def _firebase_ready() -> bool:
    try:
        import firebase_admin
        from firebase_admin import initialize_app

        if firebase_admin._apps:
            return True
        credential = _load_firebase_credential()
        if credential is None:
            logger.info("Push notification skipped: no Firebase credentials configured.")
            return False
        initialize_app(credential)
        return True
    except Exception:
        logger.exception("Failed to initialize Firebase push service.")
        return False


def upsert_push_device(
    user,
    *,
    token: str,
    platform: str = PushDevice.Platform.UNKNOWN,
    device_id: Optional[str] = None,
    app_version: Optional[str] = None,
    notify_registration_open: Optional[bool] = None,
    notify_league_started: Optional[bool] = None,
    notify_active_player: Optional[bool] = None,
) -> PushDevice:
    with transaction.atomic():
        device, _ = PushDevice.objects.select_for_update().get_or_create(
            token=token,
            defaults={
                "user": user,
                "platform": platform or PushDevice.Platform.UNKNOWN,
                "device_id": device_id,
                "app_version": app_version,
                "is_active": True,
            },
        )

        changed = False
        if device.user_id != user.id:
            device.user = user
            changed = True

        if platform and device.platform != platform:
            device.platform = platform
            changed = True
        if device.device_id != device_id:
            device.device_id = device_id
            changed = True
        if app_version is not None and device.app_version != app_version:
            device.app_version = app_version
            changed = True
        if not device.is_active:
            device.is_active = True
            changed = True

        if notify_registration_open is not None:
            device.notify_registration_open = notify_registration_open
            changed = True
        if notify_league_started is not None:
            device.notify_league_started = notify_league_started
            changed = True
        if notify_active_player is not None:
            device.notify_active_player = notify_active_player
            changed = True

        if changed:
            device.save()
        return device


def deactivate_push_device(user, token: Optional[str] = None) -> int:
    qs = PushDevice.objects.filter(user=user, is_active=True)
    if token:
        qs = qs.filter(token=token)
    return qs.update(is_active=False)


def send_push_to_devices(
    *,
    devices,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> int:
    tokens = list(devices.filter(is_active=True).values_list("token", flat=True))
    if not tokens:
        return 0
    if not _firebase_ready():
        return 0

    try:
        from firebase_admin import messaging

        total = 0
        payload = {k: str(v) for k, v in (data or {}).items()}
        for chunk in _split_chunks(tokens):
            response = messaging.send_each_for_multicast(
                messaging.MulticastMessage(
                    notification=messaging.Notification(title=title, body=body),
                    data=payload,
                    tokens=chunk,
                )
            )
            total += response.success_count
        return total
    except Exception:
        logger.exception("Failed to send push notification.")
        return 0


def notify_registration_open(season) -> int:
    devices = PushDevice.objects.filter(is_active=True, notify_registration_open=True)
    return send_push_to_devices(
        devices=devices,
        title="Liga Anmeldung geöffnet",
        body=f"Die Anmeldung für {season.name} ist jetzt offen.",
        data={
            "event": "registration_open",
            "season_id": season.id,
            "season_name": season.name,
        },
    )


def notify_league_started_active_players(season) -> int:
    devices = PushDevice.objects.filter(
        is_active=True,
        notify_league_started=True,
        user__profile__season_participants__season=season,
        user__profile__season_participants__id__in=season.leagues.values_list(
            "active_player_id", flat=True
        ),
    ).distinct()
    return send_push_to_devices(
        devices=devices,
        title="Liga gestartet",
        body=f"Die Liga in {season.name} ist gestartet und du bist als Erstes dran.",
        data={
            "event": "league_started_active_player",
            "season_id": season.id,
            "season_name": season.name,
        },
    )


def notify_active_player_turn(league, participant) -> int:
    if participant is None or not getattr(participant, "profile", None):
        return 0
    user = getattr(participant.profile, "user", None)
    if user is None:
        return 0
    devices = PushDevice.objects.filter(
        user=user,
        is_active=True,
        notify_active_player=True,
    )
    return send_push_to_devices(
        devices=devices,
        title="Du bist dran",
        body=f"In Liga L{league.level} bist du jetzt der aktive Spieler.",
        data={
            "event": "active_player_turn",
            "league_id": league.id,
            "league_level": league.level,
            "season_id": league.season_id,
        },
    )
