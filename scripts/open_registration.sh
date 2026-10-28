#!/bin/bash
set -e

# Resolve script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"

# Determine python executable
if [ -n "$VENV_PYTHON" ] && [ -x "$VENV_PYTHON" ]; then
    PYTHON_CMD="$VENV_PYTHON"
elif [ -x "$API_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$API_DIR/.venv/bin/python"
elif [ -x "$HOME/.virtualenvs/kennerliga-venv/bin/python" ]; then
    PYTHON_CMD="$HOME/.virtualenvs/kennerliga-venv/bin/python"
else
    PYTHON_CMD="python3"
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-django_rest.settings_production}"
cd "$API_DIR"

# If arguments are passed, forward them; otherwise run with 7-day check
if [ "$#" -gt 0 ]; then
    "$PYTHON_CMD" prod_manage.py open_next_season "$@"
else
    "$PYTHON_CMD" prod_manage.py open_next_season --check-7-days
fi

