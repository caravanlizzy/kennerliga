#!/bin/bash
set -e

# Path to your project and virtualenv
PROJECT_DIR="/home/haligh/kennerliga/api"
VENV_PYTHON="/home/haligh/.virtualenvs/kennerliga-venv/bin/python"

# Calculate the first day of the next month
FIRST_DAY_NEXT_MONTH=$(date -d "$(date +%Y-%m-01) +1 month" +%s)
# Calculate today's date in seconds
TODAY=$(date +%s)

# Calculate difference in days
DIFF_DAYS=$(( (FIRST_DAY_NEXT_MONTH - TODAY) / 86400 ))

# Only run if we are 7 days before the next month
if [ "$DIFF_DAYS" -eq 7 ]; then
    echo "Running open_next_season, 7 days before next month..."
    export DJANGO_SETTINGS_MODULE="django_rest.settings_production"
    "$VENV_PYTHON" "$PROJECT_DIR/prod_manage.py" open_next_season
else
    echo "Not 7 days before the next month (today is $DIFF_DAYS days away). Skipping."
fi

