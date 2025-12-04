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

class UserInviteLink(models.Model):
    key = models.CharField(max_length=32, unique=True, db_index=True)
    label = models.CharField(max_length=300, blank=True,
              help_text="Admin note to remember who this invite is for.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invite_links",
    )
    player_profile = models.ForeignKey(
        'PlayerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invite_links",
        help_text="Optional: Link this invite to an existing PlayerProfile"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(20)
        if not self.expires_at:
            self.expires_at = timezone.now() + relativedelta(months=1)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() > self.expires_at)


class Feedback(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
