import logging
from typing import Any, Dict, List, Optional

from season.models import Season, SeasonParticipant
from user.models import PlayerProfile


PICKS_WEIGHT = 0.075
BANS_WEIGHT = 0.075
REPORTS_WEIGHT = 0.850


def calculate_season_progress_from_leagues_progress(
    leagues_progress: Dict[int, Dict[str, Any]],
    is_done: bool = False,
) -> Dict[str, Any]:
    """
    Computes weighted season progress based on aggregated league progress.
    Picking and banning usually take ~2 days while playing takes the rest (~28 days),
    so posted games (reports) carry 85% of total progress, while picks (7.5%)
    and bans (7.5%) carry the remaining 15%.
    """
    total_picks_curr = 0
    total_picks_tot = 0
    total_picks_mis = 0

    total_bans_curr = 0
    total_bans_tot = 0
    total_bans_mis = 0

    total_reports_curr = 0
    total_reports_tot = 0
    total_reports_mis = 0

    for prog in leagues_progress.values():
        p = prog.get("picks", {})
        total_picks_curr += p.get("current", 0)
        total_picks_tot += p.get("total", 0)
        total_picks_mis += p.get("missing", 0)

        b = prog.get("bans", {})
        total_bans_curr += b.get("current", 0)
        total_bans_tot += b.get("total", 0)
        total_bans_mis += b.get("missing", 0)

        r = prog.get("reports", {})
        total_reports_curr += r.get("current", 0)
        total_reports_tot += r.get("total", 0)
        total_reports_mis += r.get("missing", 0)

    if is_done:
        percentage = 100.0
    elif total_picks_tot == 0 and total_bans_tot == 0 and total_reports_tot == 0:
        percentage = 0.0
    else:
        picks_ratio = (
            min(1.0, total_picks_curr / total_picks_tot)
            if total_picks_tot > 0
            else 0.0
        )
        bans_ratio = (
            min(1.0, total_bans_curr / total_bans_tot)
            if total_bans_tot > 0
            else 0.0
        )
        reports_ratio = (
            min(1.0, total_reports_curr / total_reports_tot)
            if total_reports_tot > 0
            else 0.0
        )

        weighted_val = (
            PICKS_WEIGHT * picks_ratio
            + BANS_WEIGHT * bans_ratio
            + REPORTS_WEIGHT * reports_ratio
        ) * 100.0

        if (
            total_picks_mis == 0
            and total_bans_mis == 0
            and total_reports_mis == 0
            and total_reports_tot > 0
        ):
            percentage = 100.0
        else:
            percentage = round(weighted_val, 1)

    return {
        "percentage": percentage,
        "picks": {
            "current": total_picks_curr,
            "total": total_picks_tot,
            "missing": total_picks_mis,
        },
        "bans": {
            "current": total_bans_curr,
            "total": total_bans_tot,
            "missing": total_bans_mis,
        },
        "reports": {
            "current": total_reports_curr,
            "total": total_reports_tot,
            "missing": total_reports_mis,
        },
    }


def get_seasons_progress(seasons: List[Season]) -> Dict[int, Dict[str, Any]]:
    """
    Computes progress for multiple seasons in bulk with minimal SQL queries.
    """
    if not seasons:
        return {}

    from league.models import League
    from league.queries import get_leagues_progress

    season_ids = [s.id for s in seasons]
    leagues = list(League.objects.filter(season_id__in=season_ids))

    leagues_by_season: Dict[int, List[League]] = {sid: [] for sid in season_ids}
    for lg in leagues:
        if lg.season_id in leagues_by_season:
            leagues_by_season[lg.season_id].append(lg)

    all_leagues_progress = get_leagues_progress(leagues)

    result = {}
    for season in seasons:
        season_leagues = leagues_by_season.get(season.id, [])
        season_leagues_prog = {
            lg.id: all_leagues_progress.get(
                lg.id,
                {
                    "picks": {"current": 0, "total": 0, "missing": 0},
                    "bans": {"current": 0, "total": 0, "missing": 0},
                    "reports": {"current": 0, "total": 0, "missing": 0},
                },
            )
            for lg in season_leagues
        }
        is_done = season.status == Season.SeasonStatus.DONE or season.is_completed
        result[season.id] = calculate_season_progress_from_leagues_progress(
            season_leagues_prog,
            is_done=is_done,
        )

    return result


def get_season_progress(season: Optional[Season]) -> Dict[str, Any]:
    """
    Computes progress for a single season.
    """
    if not season:
        return {
            "percentage": 0.0,
            "picks": {"current": 0, "total": 0, "missing": 0},
            "bans": {"current": 0, "total": 0, "missing": 0},
            "reports": {"current": 0, "total": 0, "missing": 0},
        }
    return get_seasons_progress([season]).get(
        season.id,
        {
            "percentage": 0.0,
            "picks": {"current": 0, "total": 0, "missing": 0},
            "bans": {"current": 0, "total": 0, "missing": 0},
            "reports": {"current": 0, "total": 0, "missing": 0},
        },
    )


def get_running_season() -> Season:
    """
    Retrieves the currently running season, if any.
    """
    return Season.objects.filter(status=Season.SeasonStatus.RUNNING).first()


def get_open_season() -> Season:
    """
    Retrieves the season with an open registration, if any.
    """
    return Season.objects.filter(status=Season.SeasonStatus.OPEN).first()


def get_previous_season() -> Season:
    """
    Retrieves the most recently completed season.
    """
    return (
        Season.objects.filter(status=Season.SeasonStatus.DONE)
        .order_by("-year", "-month")
        .first()
    )


def get_participants(season_name: str) -> List[PlayerProfile]:
    """
    Retrieves all participants of a season by the year (name).
    Assumes that season_name corresponds to the year.
    """
    try:
        season = Season.objects.get(year=season_name)
        participants = SeasonParticipant.objects.filter(season=season)
        return list(participants)
    except Season.DoesNotExist:
        logging.warning(f"No season found with year: {season_name}")
        return []


def get_registered_participants(season=None) -> List[SeasonParticipant]:
    """
    Returns all participants registered in the given or current open season.
    If no season is provided and no season is open, returns an empty list.
    """
    if not season:
        season = get_open_season()
    if season:
        participants = SeasonParticipant.objects.filter(season=season)
        return list(participants)
    else:
        logging.info("No open season found.")
        return []


def register(profile):
    """
    Registers a player profile for the current open season.

    Returns the created SeasonParticipant, or ``None`` when no season is
    currently open for registration. ``SeasonParticipant.season`` is not
    nullable, so creating one without an open season would raise an
    IntegrityError.
    """
    open_season = get_open_season()
    if not open_season:
        logging.info("No open season found; registration skipped.")
        return None
    new_participant = SeasonParticipant(season=open_season, profile=profile)
    new_participant.save()
    return new_participant


def is_profile_registered(profile, season):
    """
    Checks if a player profile is registered for a specific season.
    """
    return SeasonParticipant.objects.filter(season=season, profile=profile).exists()
