#!/bin/bash
set -e

# Path to your project and virtualenv
PROJECT_DIR="/home/haligh/kennerliga/api"
VENV_PYTHON="/home/haligh/.virtualenvs/kennerliga-venv/bin/python"

# Run the start new season command only on the last day of the month
if [ "$(date -d "+1 day" +%d)" = "01" ]; then
    export DJANGO_SETTINGS_MODULE="django_rest.settings_production"
    "$VENV_PYTHON" "$PROJECT_DIR/prod_manage.py" start_new_season
else
    echo "Today is not the last day of the month. Skipping season creation."
fi
