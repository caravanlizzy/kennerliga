"""
Read helpers for the app-wide configuration.

These are the single entry points the rest of the codebase should use to
read a configurable setting, so callers never have to know whether a value
comes from a stored :class:`~configuration.models.AppConfiguration` version
or from the hard-coded fallback in ``api.constants``.
"""
from api.constants import MAX_SAME_GAME_PER_YEAR
from configuration.models import AppConfiguration


def get_max_same_game_per_year() -> int:
    """
    Returns the currently configured limit for how many times the same game
    may be picked per year, falling back to the ``api.constants`` default
    when the app has not been configured yet.
    """
    config = AppConfiguration.current()
    if config is not None:
        return config.max_same_game_per_year
    return MAX_SAME_GAME_PER_YEAR


def get_tie_decider_game():
    """
    Returns the ``game.Game`` configured as the tie-decider (the game played
    to decide a league), or ``None`` if none is configured.
    """
    config = AppConfiguration.current()
    return config.tie_decider_game if config is not None else None
