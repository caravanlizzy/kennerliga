from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.functions import Lower

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


class UserInvitation(models.Model):
    username = models.CharField(max_length=44, db_index=True)
    otp = models.CharField(max_length=10)
    failed_attempts = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation for {self.username} (by {self.created_by})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['username'], name='unique_invite_per_username'
            )
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