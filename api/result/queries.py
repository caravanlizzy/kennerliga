from typing import Optional
from django.db.models import QuerySet
from result.models import Result
from league.models import League
from season.models import Season


def get_results_for_league(league: League) -> QuerySet:
    """
    Returns all results recorded for a specific league.
    """
    return Result.objects.filter(league=league)


def get_results_for_season(season: Season) -> QuerySet:
    """
    Returns all results recorded for a specific season.
    """
    return Result.objects.filter(season=season)


def get_results_for_selected_game(selected_game) -> QuerySet:
    """
    Returns all results recorded for a specific selected game.
    """
    return Result.objects.filter(selected_game=selected_game)


def get_result_by_id(result_id: int) -> Optional[Result]:
    """
    Retrieves a Result object by its ID.
    """
    return Result.objects.filter(id=result_id).first()
