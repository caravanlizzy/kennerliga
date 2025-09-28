import hashlib
import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class User(AbstractUser):
    # remove inherited first_name/last_name
    first_name = None
    last_name = None

    # Re-declare username with your length but keep validators & uniqueness
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=44,
        unique=True,
        blank=False,
        null=False,
        help_text='Username is used to login',
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.username)


class Platform(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='uniq_platform_name_ci'),
        ]


class PlayerProfile(models.Model):
    profile_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile')
    platforms = models.ManyToManyField(Platform, through='PlatformPlayer')

    def __str__(self):
        return self.profile_name


class PlatformPlayer(models.Model):
    player_profile = models.ForeignKey(
        PlayerProfile, on_delete=models.CASCADE, related_name='platform_links'
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name='player_links'
    )
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('player_profile', 'platform'),
                name='uniq_profile_platform',
            )
        ]

    def __str__(self):
        return f"{self.player_profile} @ {self.platform} as {self.name}"


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class UserInviteLink(models.Model):
    # store only the hash; share the raw key in the URL
    key_hash   = models.CharField(max_length=64, unique=True, db_index=True)
    label      = models.CharField(max_length=100, blank=True,
                   help_text="Admin note to remember who this invite is for.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invite_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # only set expires_at if it isn't already provided
        if not self.expires_at:
            self.expires_at = timezone.now() + relativedelta(months=1)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() > self.expires_at)

    @classmethod
    def create_with_random_key(cls, *, created_by, label="", expires_at=None):
        raw = secrets.token_urlsafe(20)   # URL-safe secret
        obj = cls.objects.create(
            key_hash=_hash_key(raw),
            label=label,
            created_by=created_by,
            expires_at=expires_at,
        )
        return obj, raw  # return the raw key so you can share it
