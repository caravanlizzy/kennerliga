from season_manager import create_new_season, is_new_season_due, is_first_day_of_month

# create a season if due which is open to registration
if is_new_season_due():
    create_new_season()

if is_first_day_of_month():
    setup_leagues()

