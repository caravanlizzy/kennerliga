from organisation.organize import Organize

organize = Organize()

# create new season if
if organize.check_new_season():
    organize.create_season()

