from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional, Tuple, Any

from django.db import transaction
from django.db.models import Min

from game.models import SelectedGame
from result.models import Result, EloChange
from user.models import PlayerProfile

logger = logging.getLogger(__name__)

INITIAL_ELO: float = 1500.0
K_FACTOR: float = 32.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """
    Computes the expected score of player A against player B based on their Elo ratings.
    """
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def actual_score(position_a: int, position_b: int) -> float:
    """
    Computes the head-to-head match outcome between two finishing positions.
    1.0 if player A finished ahead of player B.
    0.0 if player A finished behind player B.
    0.5 if tied.
    """
    if position_a < position_b:
        return 1.0
    if position_a > position_b:
        return 0.0
    return 0.5


def calculate_multiplayer_elo(
    results: Iterable[Any],
    current_ratings: Optional[Dict[int, float]] = None,
) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Calculates pairwise multiplayer Elo adjustments for a single match.
    Averages pairwise deltas across opponents so that matches with different player counts
    have comparable impact.

    Args:
        results: List of objects or dicts representing match placements.
                 Must have `player_profile_id` (or `profile_id`) and `position`.
        current_ratings: Dict of {player_profile_id: rating}. Defaults to INITIAL_ELO if omitted.

    Returns:
        (new_ratings, deltas):
          new_ratings: {player_profile_id: new_rating}
          deltas: {player_profile_id: delta}
    """
    if current_ratings is None:
        current_ratings = {}

    parsed_results = []
    for r in results:
        pid = getattr(r, "player_profile_id", None)
        if pid is None:
            pid = getattr(r, "profile_id", None)
        if pid is None and isinstance(r, dict):
            pid = r.get("player_profile_id", r.get("profile_id", r.get("player_id")))
        
        pos = getattr(r, "position", None)
        if pos is None and isinstance(r, dict):
            pos = r.get("position")

        if pid is not None and pos is not None:
            parsed_results.append({"player_profile_id": pid, "position": pos})

    if len(parsed_results) < 2:
        return {}, {}

    deltas: Dict[int, float] = {}

    for item_a in parsed_results:
        player_a = item_a["player_profile_id"]
        pos_a = item_a["position"]
        rating_a = float(current_ratings.get(player_a, INITIAL_ELO))

        total_delta = 0.0
        opponents = [r for r in parsed_results if r["player_profile_id"] != player_a]

        for item_b in opponents:
            player_b = item_b["player_profile_id"]
            pos_b = item_b["position"]
            rating_b = float(current_ratings.get(player_b, INITIAL_ELO))

            exp = expected_score(rating_a, rating_b)
            act = actual_score(pos_a, pos_b)

            total_delta += K_FACTOR * (act - exp)

        deltas[player_a] = total_delta / max(len(opponents), 1)

    new_ratings = {
        player_id: float(current_ratings.get(player_id, INITIAL_ELO)) + delta
        for player_id, delta in deltas.items()
    }

    return new_ratings, deltas


def apply_elo_for_selected_game(selected_game: SelectedGame) -> List[EloChange]:
    """
    Calculates and applies Elo rating changes for a finalized selected game.
    Deletes any previously calculated EloChange entries for this game and creates new ones,
    then updates the PlayerProfile.elo_rating values.
    """
    results = list(
        Result.objects.filter(
            selected_game=selected_game, position__isnull=False
        ).select_related("player_profile", "league__season")
    )

    if len(results) < 2:
        return []

    with transaction.atomic():
        # Clean up any existing EloChange for this match
        EloChange.objects.filter(selected_game=selected_game).delete()

        current_ratings = {
            r.player_profile_id: getattr(r.player_profile, "elo_rating", INITIAL_ELO) or INITIAL_ELO
            for r in results
        }

        new_ratings, deltas = calculate_multiplayer_elo(results, current_ratings)

        created_changes = []
        for r in results:
            pid = r.player_profile_id
            if pid not in deltas:
                continue

            change = EloChange.objects.create(
                player_profile_id=pid,
                selected_game=selected_game,
                season=selected_game.league.season,
                league=selected_game.league,
                rating_before=current_ratings[pid],
                rating_after=new_ratings[pid],
                delta=deltas[pid],
            )
            created_changes.append(change)

            PlayerProfile.objects.filter(id=pid).update(elo_rating=new_ratings[pid])
            if r.player_profile:
                r.player_profile.elo_rating = new_ratings[pid]

        return created_changes


def rebuild_all_elo() -> int:
    """
    Recalculates Elo ratings for all historical matches in chronological order from scratch.
    Resets all PlayerProfile.elo_rating to INITIAL_ELO, clears EloChange history, and
    reapplies multiplayer Elo sequentially.

    Returns:
        The total number of matches (SelectedGame instances) processed.
    """
    with transaction.atomic():
        # Reset all profiles
        PlayerProfile.objects.all().update(elo_rating=INITIAL_ELO)
        EloChange.objects.all().delete()

        # Find all selected games with at least two completed results
        # Order chronologically by Season (year, month), earliest result created_at, selected_game created_at, id
        matches_qs = (
            SelectedGame.objects.filter(result__position__isnull=False)
            .annotate(min_result_time=Min("result__created_at"))
            .select_related("league__season")
            .order_by(
                "league__season__year",
                "league__season__month",
                "league__level",
                "min_result_time",
                "created_at",
                "id",
            )
            .distinct()
        )

        ratings_map: Dict[int, float] = {
            profile_id: INITIAL_ELO
            for profile_id in PlayerProfile.objects.values_list("id", flat=True)
        }

        elo_changes_to_create: List[EloChange] = []
        processed_matches_count = 0

        for sg in matches_qs:
            results = list(
                Result.objects.filter(selected_game=sg, position__isnull=False)
            )
            if len(results) < 2:
                continue

            new_ratings, deltas = calculate_multiplayer_elo(results, ratings_map)
            if not deltas:
                continue

            for r in results:
                pid = r.player_profile_id
                if pid not in deltas:
                    continue

                rating_before = ratings_map.get(pid, INITIAL_ELO)
                rating_after = new_ratings[pid]
                delta = deltas[pid]

                elo_changes_to_create.append(
                    EloChange(
                        player_profile_id=pid,
                        selected_game=sg,
                        season=sg.league.season,
                        league=sg.league,
                        rating_before=rating_before,
                        rating_after=rating_after,
                        delta=delta,
                        created_at=r.created_at,
                    )
                )

                ratings_map[pid] = rating_after

            processed_matches_count += 1

        if elo_changes_to_create:
            EloChange.objects.bulk_create(elo_changes_to_create)

        for pid, final_rating in ratings_map.items():
            PlayerProfile.objects.filter(id=pid).update(elo_rating=final_rating)

        return processed_matches_count


def get_elo_rank(profile: Optional[PlayerProfile]) -> Optional[int]:
    """
    Returns the 1-based Elo rank of the given player profile across all player profiles.
    """
    if profile is None or getattr(profile, "elo_rating", None) is None:
        return None
    return PlayerProfile.objects.filter(elo_rating__gt=profile.elo_rating).count() + 1
