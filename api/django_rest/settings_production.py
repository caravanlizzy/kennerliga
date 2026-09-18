from .settings import *  # noqa: F401,F403

DEBUG = env_bool("DEBUG", False)

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL", False)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
