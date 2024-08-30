from manager.season_manager import SeasonManager

season_manager = SeasonManager()

# create new season if
if season_manager.check_new_season():
    season_manager.create_season()

