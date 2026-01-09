from django.db import transaction
from game.models import SelectedGame, SelectedOption, BanDecision
from league.services import advance_turn

def create_selected_game(game, league, profile, selected_options_data, manage_only=False):
    with transaction.atomic():
        selected_game = SelectedGame.objects.create(
            game=game,
            league=league,
            profile=profile
        )
        
        for option_data in selected_options_data:
            SelectedOption.objects.create(
                selected_game=selected_game,
                **option_data
            )
            
        if not manage_only and league:
            advance_turn(league)
            
        return selected_game

def create_ban_decision(league, profile, game=None, selected_game=None, manage_only=False):
    with transaction.atomic():
        ban_decision, _ = BanDecision.objects.update_or_create(
            league=league,
            player_banning=profile,
            defaults={
                'game': game,
                'selected_game': selected_game
            }
        )
        
        if not manage_only and league:
            advance_turn(league)
            
        return ban_decision
