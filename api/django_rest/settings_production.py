import os
from pathlib import Path
from dotenv import load_dotenv

# Adjust BASE_DIR to where your .env is
# If .env is next to manage.py:
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env BEFORE importing base settings and BEFORE using os.getenv
load_dotenv(BASE_DIR / ".env")

from .settings import *  # noqa: E402, F401

SECRET_KEY = os.getenv("SECRET_KEY")

FRONTEND_REGISTER_URL = 'www.kennerliga.de/#/register'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        # never allow None here, fall back to something sensible
        'HOST': os.getenv("DB_HOST") or "127.0.0.1",
        # optional but recommended:
        'PORT': os.getenv("DB_PORT") or "3306",
    }
}
