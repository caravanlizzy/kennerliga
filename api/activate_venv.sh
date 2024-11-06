#!/bin/bash

# Check if the .venv directory exists
if [ -d ".venv" ]; then
    # Activate the virtual environment
    source .venv/bin/activate
    echo "Virtual environment activated."
else
    echo "Error: .venv directory not found."
fi

