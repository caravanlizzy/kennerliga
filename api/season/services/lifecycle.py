import logging
from typing import List

from league.models import League
from league.services import set_league_active_player
from season.models import Season


def close_season(season: Season):
    """
    Marks the given season as DONE.
    """
    if not season:
        return None
    season.status = Season.SeasonStatus.DONE
    season.save()
    return season


def start_open_season(season: Season):
    """
    Changes the status of an OPEN season to RUNNING.
    """
    if not season:
        raise ValueError("No season provided")
    if season.status != Season.SeasonStatus.OPEN:
        raise ValueError(
            f"Season with status '{season.status}' cannot be started."
        )
    season.status = Season.SeasonStatus.RUNNING
    season.save()
    return season


def create_next_season(current_season: Season) -> Season:
    """
    Creates a new season for the month following the given current season.
    """
    if not current_season:
        raise ValueError("No running season found")
    new_month, new_year = _next_month_year(current_season.month, current_season.year)
    new = Season(year=new_year, month=new_month, status=Season.SeasonStatus.NEXT)
    new.save()
    return new


def open_registration(season: Season) -> Season:
    """
    Changes the status of a season to OPEN, allowing players to register,
    creates the registration announcement, and sends push notifications.
    """
    if not season:
        raise ValueError("No season provided")
    if season.status not in (Season.SeasonStatus.NEXT, Season.SeasonStatus.OPEN):
        raise ValueError(
            f"Season with status '{season.status}' cannot be opened for registration."
        )

    season.status = Season.SeasonStatus.OPEN
    season.save()

    # Create announcement if not exists
    from announcement.models import Announcement
    from datetime import timedelta

    next_month_start = season.season_start_time
    visible_from = next_month_start - timedelta(days=7)
    visible_until = next_month_start
    title = f"Sign Up Season {season.month}"

    exists = Announcement.objects.filter(
        type=Announcement.AnnouncementType.REGISTER,
        title=title,
        visible_until=visible_until,
    ).exists()

    if not exists:
        Announcement.objects.create(
            type=Announcement.AnnouncementType.REGISTER,
            title=title,
            content="",
            visible_from=visible_from,
            visible_until=visible_until,
        )

    try:
        from notification.services import notify_all_users

        notify_all_users(
            "Season registration is open",
            f"Registration for {season.name} is now open.",
            "/#/register",
        )
    except Exception as e:
        logging.warning(f"Failed to send push notification on open registration: {e}")

    return season


def create_leagues(season: Season, participants: List) -> List[League]:
    """
    Distributes participants into leagues for the given season and sets the first active player for each.
    """
    players_per_league = _players_per_league(len(participants))
    leagues = [
        League.objects.create(season=season, level=i + 1)
        for i in range(len(players_per_league))
    ]
    counter = 0

    for league, size in zip(leagues, players_per_league):
        first_participant = None
        for i in range(size):
            participant = participants[counter]
            league.members.add(participant)
            if i == 0:
                first_participant = participant
            counter += 1

        if first_participant is not None:
            set_league_active_player(league, first_participant)

    return leagues


def _next_month_year(month: int, year: int):
    """
    Helper to calculate the next month and year.
    """
    return (1, year + 1) if month == 12 else (month + 1, year)


def _players_per_league(count: int) -> List[int]:
    """
    Calculates the number of players per league based on the total participant count.
    Aiming for 4 players per league, with fallback to 3 or 2.
    """
    league_count, rest = divmod(count, 4)
    players = [4] * league_count
    if rest == 1:
        if league_count > 0:
            players[-1] = 3
        players.append(2)
    elif rest == 2:
        players.append(2)
    elif rest == 3:
        players.append(3)
    return players
