"""
Helpers to build a fully-prefetched ``SeasonParticipant`` queryset and to stash
per-league lookup tables on the league object.

The goal is to make :class:`season.serializer.SeasonParticipantSerializer` read
all per-row data from prefetched attributes / context lookups, avoiding the
N+1 query storm that previously occurred for every member of every league.

Two attach points are used by the serializer:

1. **Per-profile prefetched lists** attached via ``Prefetch(..., to_attr=...)``
   on the related ``PlayerProfile``:

   * ``profile.sg_in_league``   -> list[SelectedGame] for this league
   * ``profile.bans_in_league`` -> list[BanDecision]  made by this profile in this league

2. **Per-league lookup tables** attached directly on the ``League`` instance
   (which must also be put into the serializer context as ``"league"``):

   * ``league._standings_order`` -> list[profile_id] in standings order
   * ``league._active_player_id``-> id of the active SeasonParticipant (or ``None``)

The latter avoids re-querying ``LeagueStanding`` and re-loading
``league.active_player`` once per rendered participant.
"""
from __future__ import annotations

from typing import Iterable, Optional

from django.db.models import Exists, OuterRef, Prefetch, QuerySet

from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStanding
from season.models import SeasonParticipant


def build_members_queryset(league: League) -> QuerySet[SeasonParticipant]:
    """
    Return a ``SeasonParticipant`` queryset for ``league.members`` with every
    piece of per-row data the participant serializer needs already prefetched
    or annotated. Result is ordered by ``rank, id``.
    """
    return (
        league.members.select_related("profile__user", "season")
        .prefetch_related(
            Prefetch(
                "profile__selected_games",
                queryset=SelectedGame.objects.filter(league=league).select_related(
                    "game"
                ),
                to_attr="sg_in_league",
            ),
            Prefetch(
                "profile__ban_decisions",
                queryset=BanDecision.objects.filter(league=league).select_related(
                    "selected_game__game"
                ),
                to_attr="bans_in_league",
            ),
        )
        .annotate(
            has_banned=Exists(
                BanDecision.objects.filter(
                    league=league,
                    player_banning_id=OuterRef("profile_id"),
                )
            )
        )
        .order_by("rank", "id")
    )


def attach_league_lookups(league: League) -> League:
    """
    Compute and attach lookup data needed by ``SeasonParticipantSerializer`` to
    the ``league`` instance, so that per-row serializer methods stay O(1).

    Adds:

    * ``league._standings_order``  -> list of ``player_profile_id`` ordered by
      ``-league_points, -wins, -tie_break_priority, profile_name``.
    * ``league._active_player_id`` -> the SeasonParticipant id of the active
      player, or ``None``.

    Safe to call multiple times; later calls overwrite previous values.
    """
    league._standings_order = list(
        LeagueStanding.objects.filter(league=league)
        .order_by(
            "-league_points",
            "-wins",
            "-tie_break_priority",
            "player_profile__profile_name",
        )
        .values_list("player_profile_id", flat=True)
    )
    # ``active_player_id`` is a plain FK column -> no extra query.
    league._active_player_id = league.active_player_id
    return league


def prefetched_members(league: League) -> Iterable[SeasonParticipant]:
    """
    Convenience: return an iterable of fully-prefetched members for ``league``
    and attach the per-league lookup tables. The returned iterable is a list,
    so it can be passed to the serializer without triggering a second query.
    """
    attach_league_lookups(league)
    return list(build_members_queryset(league))


def get_league_standings_order(league: Optional[League]) -> list[int]:
    """
    Return the cached standings order if present, otherwise compute it on the
    fly. Centralizes the fallback so callers/serializers don't duplicate it.
    """
    if league is None:
        return []
    cached = getattr(league, "_standings_order", None)
    if cached is not None:
        return cached
    attach_league_lookups(league)
    return league._standings_order
