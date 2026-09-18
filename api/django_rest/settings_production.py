import os
from pathlib import Path
from dotenv import load_dotenv

# Adjust BASE_DIR to where your .env is
# If .env is next to manage.py:
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env BEFORE importing base settings and BEFORE using os.getenv
load_dotenv(BASE_DIR / ".env")

from .settings import *  # noqa: E402, F401

SECRET_KEY = os.getenv("SECRET_KEY", SECRET_KEY)
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

FRONTEND_REGISTER_URL = "www.kennerliga.de/#/register"
