from typing import Optional
from django.db.models import QuerySet, Max
from result.models import Result
from league.models import League
from season.models import Season
from game.models import ResultConfig


def get_game_records_map() -> dict[int, int]:
    """
    Returns a dict mapping game_id -> max_score (int) for games with point scoring
    where max_score >= 2.
    """
    no_points_game_ids = set(
        ResultConfig.objects.filter(has_points=False).values_list("game_id", flat=True)
    )
    records = (
        Result.objects.filter(points__gte=2)
        .exclude(selected_game__game_id__in=no_points_game_ids)
        .values("selected_game__game_id")
        .annotate(max_points=Max("points"))
    )
    return {r["selected_game__game_id"]: r["max_points"] for r in records}


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
