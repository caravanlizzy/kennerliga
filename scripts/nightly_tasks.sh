#!/bin/bash
set -e

# Path to your project and virtualenv
PROJECT_DIR="/home/haligh/kennerliga/api"
VENV_PYTHON="/home/haligh/.virtualenvs/kennerliga-venv/bin/python"

# 1) Run the backup command
export DJANGO_SETTINGS_MODULE="django_rest.settings_production"
"$VENV_PYTHON" "$PROJECT_DIR/prod_manage.py" db_backup

# 2) Run season start if last day of the month
TOMORROW_DAY=$(date -d tomorrow +%d)
if [ "$TOMORROW_DAY" = "01" ]; then
    echo "Last day of the month detected, starting new season..."
    "$VENV_PYTHON" "$PROJECT_DIR/prod_manage.py" start_new_season
fi
