from django.conf import settings
from django.db import models

from api.constants import MAX_SAME_GAME_PER_YEAR as DEFAULT_MAX_SAME_GAME_PER_YEAR


class AppConfiguration(models.Model):
    """
    Global, app-wide settings editable by admins.

    Every save creates a new immutable version rather than mutating an
    existing row, so the whole change history is preserved (paired with the
    time it was applied via ``created_at``). The *current* configuration is
    therefore simply the most recently created row -- see ``current``.
    """

    # Max number of times the same game (including related games) may be
    # picked by a player within a single year. Historically 2, was 3 once.
    max_same_game_per_year = models.PositiveIntegerField(
        default=DEFAULT_MAX_SAME_GAME_PER_YEAR
    )
    # The game that is played to decide a league when a tie has to be broken
    # (historically "Cant Stop"). Nullable so the app still works before an
    # admin has picked one; ``SET_NULL`` keeps old config versions valid if
    # the referenced game is ever deleted.
    tie_decider_game = models.ForeignKey(
        "game.Game",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"AppConfiguration #{self.id} ({self.created_at:%Y-%m-%d %H:%M})"

    @classmethod
    def current(cls):
        """Returns the most recent configuration version, or ``None`` if the
        app has never been configured yet."""
        return cls.objects.order_by("-created_at", "-id").first()
