from django.db import transaction
from game.models import SelectedGame, SelectedOption, BanDecision
from league.services import advance_turn


def create_selected_game(
    game, league, profile, selected_options_data, manage_only=False
):
    """
    Creates a SelectedGame along with its associated SelectedOptions.
    Automatically advances the league's turn unless manage_only is True.
    """
    with transaction.atomic():
        selected_game = SelectedGame.objects.create(
            game=game, league=league, profile=profile
        )

        for option_data in selected_options_data:
            SelectedOption.objects.create(selected_game=selected_game, **option_data)

        if not manage_only and league:
            advance_turn(league)

        return selected_game


def create_ban_decision(league, profile, selected_game=None, manage_only=False):
    """
    Records a player's ban decision for a league.
    Automatically advances the league's turn unless manage_only is True.
    """
    with transaction.atomic():
        ban_decision, _ = BanDecision.objects.update_or_create(
            league=league,
            player_banning=profile,
            defaults={"selected_game": selected_game},
        )

        if not manage_only and league:
            advance_turn(league)

        return ban_decision
