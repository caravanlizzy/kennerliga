from django.db import models


class Announcement(models.Model):
    """
    Model representing a system announcement or notification.
    """

    class AnnouncementType(models.TextChoices):
        """
        Choices for the type of announcement.
        """
        INFO = "INFO"
        WINNER = "WINNER"
        REGISTER = "REGISTER"
        WARNING = "WARNING"
        NEUTRAL = "NEUTRAL"

    type = models.CharField(
        max_length=20, choices=AnnouncementType.choices, default=AnnouncementType.INFO
    )

    title = models.CharField(max_length=88)

    content = models.TextField(blank=True, null=True)

    visible_until = models.DateTimeField()
    visible_from = models.DateTimeField()
