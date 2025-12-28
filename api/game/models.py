from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from user.models import PlayerProfile, Platform


class Game(models.Model):
    name = models.CharField(max_length=88)
    short_name = models.CharField(max_length=33, blank=True, default='')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'platform'],
                name='unique_game_per_platform'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GameOption(models.Model):
    name = models.CharField(max_length=88)
    game = models.ForeignKey("Game", null=True, blank=True, on_delete=models.CASCADE, related_name="options")
    has_choices = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Legacy fields (keep for now, but consider deprecating after a data migration)
    only_if_option = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="only_if_options",
    )
    only_if_choice = models.ForeignKey(
        "GameOptionChoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="only_if_options",
    )
    only_if_value = models.BooleanField(null=True, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['order']


class GameOptionChoice(models.Model):
    name = models.CharField(max_length=139, blank=True, null=True)
    option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name or '(Unnamed)'} for {self.option.name}"

    class Meta:
        ordering = ['order']


class GameOptionAvailabilityGroup(models.Model):
    """
    A group is one OR-branch.
    All conditions inside the group must match (AND).
    If any group matches, the option is available (OR across groups).
    """
    option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name="availability_groups",
    )

    def __str__(self):
        return f"Availability group for {self.option.name}"


class GameOptionAvailabilityCondition(models.Model):
    """
    A single atomic requirement inside a group.
    Exactly one of expected_value or expected_choice must be set.
    """
    group = models.ForeignKey(
        GameOptionAvailabilityGroup,
        on_delete=models.CASCADE,
        related_name="conditions",
    )

    depends_on_option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name="required_by_conditions",
    )

    expected_value = models.BooleanField(null=True, blank=True)
    expected_choice = models.ForeignKey(
        "GameOptionChoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="required_by_conditions",
    )

    negate = models.BooleanField(
        default=False,
        help_text="If true, invert the condition (NOT).",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="availability_condition_exactly_one_expected",
                check=(
                    # (expected_value is null) XOR (expected_choice is null)
                    (models.Q(expected_value__isnull=False) & models.Q(expected_choice__isnull=True))
                    | (models.Q(expected_value__isnull=True) & models.Q(expected_choice__isnull=False))
                ),
            ),
        ]

    def clean(self):
        super().clean()

        # If you set expected_choice, it must belong to depends_on_option.
        if self.expected_choice_id and self.depends_on_option_id:
            if self.expected_choice.option_id != self.depends_on_option_id:
                raise ValidationError(
                    {"expected_choice": "expected_choice must belong to depends_on_option."}
                )

    def __str__(self):
        exp = (
            f"value={self.expected_value}"
            if self.expected_choice_id is None
            else f"choice_id={self.expected_choice_id}"
        )
        prefix = "NOT " if self.negate else ""
        return f"{prefix}{self.depends_on_option.name} requires {exp}"


class SelectedGame(models.Model):
    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='selected_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_selections')
    league = models.ForeignKey("league.League", on_delete=models.CASCADE, related_name='game_selections')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['league', 'game'],
                name='unique_game_per_league'
            ),
        ]

    def __str__(self):
        return f"{self.profile}'s selection for {self.game.name}"


class SelectedOption(models.Model):
    selected_game = models.ForeignKey(SelectedGame, on_delete=models.CASCADE, related_name='selected_options')
    game_option = models.ForeignKey(GameOption, on_delete=models.CASCADE, related_name='selections')
    choice = models.ForeignKey(GameOptionChoice, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='selections')
    value = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Option: {self.game_option.name}, Choice: {self.choice.name if self.choice else 'No choice'}, Value: {self.value}"


class BanDecision(models.Model):
    league = models.ForeignKey("league.League", on_delete=models.CASCADE, related_name='ban_decisions')
    player_banning = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='ban_decisions')
    selected_game = models.ForeignKey(SelectedGame, null=True, blank=True, on_delete=models.SET_NULL)
    skipped_ban = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('league', 'player_banning')

    def __str__(self):
        return f"{self.player_banning} {'banned ' + str(self.selected_game) if self.selected_game else 'skipped banning'} in {self.league}"


class StartingPointSystem(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.code


class ResultConfig(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_asymmetric = models.BooleanField(default=False)
    has_starting_player_order = models.BooleanField(default=True)
    starting_points_system = models.ForeignKey(StartingPointSystem, on_delete=models.SET_NULL, null=True, default=1)
    has_points = models.BooleanField(default=True)

    def __str__(self):
        return f"ResultConfig for {self.game}"


class TieBreaker(models.Model):
    result_config = models.ForeignKey(ResultConfig, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(
        help_text="Higher order is more important."
    )
    higher_wins = models.BooleanField(
        default=True,
        help_text="If True, higher values win. If False, lower values win."
    )

    class Meta:
        ordering = ['-order']

    def __str__(self):
        return str(self.name)


class Faction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    level = models.PositiveIntegerField(
        default=0,
        help_text="The sequence level: 0 for Country, 1 for Leader, etc."
    )

    def __str__(self):
        return f"{self.name} (Lvl {self.level} - {self.game.name})"

    class Meta:
        ordering = ['level', 'name']
