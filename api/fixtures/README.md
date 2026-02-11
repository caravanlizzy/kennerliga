# Fixtures

This directory contains Django fixtures for the project.

## Demo Data

- **demo_data.json**: A comprehensive set of demo data including:
    - 20 Users and PlayerProfiles
    - Historical seasons from **2020-S1** up to the current month.
    - 2 Leagues per season with 4 players each.
    - **2300+ Match Results** with correct winner logic (highest points = rank 1).
    - **Lively Chat Messages**: 600+ demo chat entries including trash talk, congratulations, and announcements.
    - Automatically calculated Standings, game picks, and bans.
    - Platforms, Games, Factions, and Result Configurations.

### Loading Demo Data

To load the demo data into your local database, run:

```bash
python manage.py loaddata fixtures/demo_data.json
```

**Note**: Loading fixtures will add data to your existing database. If you want a clean state, you may want to flush the database first (caution: this deletes all current data):

```bash
python manage.py flush
python manage.py loaddata fixtures/demo_data.json
```

## Other Fixtures

- **ready_to_ban.json**: State where all players have picked games and it's time to ban.
- **bans_done.json**: State where bans are finished and it's time to play.
- **season_started.json**: State where a new season has just started.
- **open_for_registration.json**: State where a season is open for registration.
