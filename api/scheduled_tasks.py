from season_manager import SeasonManager

season_manager = SeasonManager()

# create a season if due which is open to registration
if season_manager.current_season:
    season_manager.create_new_season()

if season_manager.is_first_day_of_month():
    season_manager.start_new_season()

