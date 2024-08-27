from datetime import timezone

from django.db import models

from user.models import User


class Announcement(models.Model):
    class AnnouncementType(models.TextChoices):
        INFO = 'INFO'
        WINNER = 'WINNER'
        REGISTER = 'REGISTER'
        WARNING = 'WARNING'
        NEUTRAL = 'NEUTRAL'

    type = models.CharField(
        max_length=20,
        choices=AnnouncementType.choices,
        default=AnnouncementType.INFO
    )

    title = models.CharField(
        max_length=88
    )

    content = models.TextField(
        blank=True,
        null=True
    )

    visible_until = models.DateTimeField()
    visible_from = models.DateTimeField()
