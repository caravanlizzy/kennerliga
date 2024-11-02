#!/bin/bash

# Activate virtual environment
source api/.venv/bin/activate

# Start Django server in the background
(cd api && ./manage.py runserver) &

# Start frontend development server
(cd frontend && npm run dev)

