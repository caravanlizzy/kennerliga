from datetime import datetime, timedelta
from random import random
from typing import List, Dict

from season.models import Season
from season.service import get_running_season, get_previous_season, get_registered_participants
from user.models import PlayerProfile
from user.profile_service import get_previous_season_result, is_last


def get_new_month_year(month: int, year: int) -> (int, int):
    """Calculate the new month and year after incrementing the month."""
    new_month = month + 1
    new_year = year
    if new_month == 13:
        new_year += 1
        new_month = 1
    return new_month, new_year


def create_next_season():
    """Create the next season based on the current running season."""
    current_season = get_running_season()
    if not current_season:
        print("No seasons created so far.")
        return
    new_month, new_year = get_new_month_year(current_season.month, current_season.year)
    new_season = Season(year=new_year, month=new_month)
    new_season.save()
    print(f"Next season created: {new_season.year}-{new_season.month}")


def start_season():
    """Start the current running season."""
    season = get_running_season()
    if season:
        season.status = Season.SeasonStatus.RUNNING
        season.save()


def open_registration():
    """Open registration for the current running season."""
    season = get_running_season()
    if season:
        season.status = Season.SeasonStatus.OPEN
        season.save()


def check_new_season() -> bool:
    """Check if a new season is due to start in 7 days."""
    today = datetime.today()
    first_day_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day_this_month = first_day_next_month - timedelta(days=1)
    days_left = (last_day_this_month - today).days
    return days_left == 7


def get_previous_season_participants(participants: List[PlayerProfile]) -> List[PlayerProfile]:
    """Get participants who were registered in the previous season."""
    previous_season = get_previous_season()
    if not previous_season:
        return []  # Return an empty list if no previous season exists

    previous_participants = set(previous_season.participants.all())
    return [p for p in participants if p in previous_participants]


def apply_promotion(participants: List[Dict]) -> List[Dict]:
    """Apply promotion logic to the participants list."""
    for index in range(1, len(participants)):
        previous = participants[index - 1]
        if previous['is_last'] and participants[index]['league'] - 1 == previous['league']:
            participants[index], participants[index - 1] = participants[index - 1], participants[index]
    return participants


def order_previous_season_participants(participants: List[PlayerProfile]) -> List[Dict]:
    """Order participants based on their previous season performance."""
    default_list = [
        {
            'name': p.profile_name,
            'league': league_info['league'].level if league_info['league'] else None,
            'position': league_info['position'],
            'is_last': league_info['is_last']
        }
        for p in participants if (league_info := get_previous_season_result(p)) is not None
    ]

    sorted_list = sorted(default_list, key=lambda x: (x['league'], x['position']))
    promoted_list = apply_promotion(sorted_list)
    return promoted_list


def sort_participants() -> List[dict]:
    """Order the participants based on registration and previous participation."""
    participants = get_registered_participants()
    previously_registered = get_previous_season_participants(participants)
    new_participants = list(set(participants) - set(previously_registered))
    random.shuffle(new_participants)
    sorted_participants = order_previous_season_participants(previously_registered)
    return sorted_participants + new_participants
