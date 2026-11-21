#!/usr/bin/env python3
"""
Cron service script for Railway / scheduled jobs.
Checks midnight Europe/Berlin time:
  - If it is 7 days before the new month: runs open_next_season
  - If it is the first day of the month: runs start_new_season
"""

import os
import sys
from pathlib import Path

# Resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
API_DIR = PROJECT_ROOT / "api"

# Ensure API directory is in sys.path
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Ensure current working directory is API_DIR for Django relative paths
os.chdir(API_DIR)

# Set Django settings module if not already set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_rest.settings_production")

try:
    import django
    django.setup()
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Ensure dependencies are installed and virtual environment is active."
    ) from exc

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    args = ["manage.py", "cron_season_job"] + sys.argv[1:]
    execute_from_command_line(args)
