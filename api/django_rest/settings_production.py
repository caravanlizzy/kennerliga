import os
from .settings import *

SECRET_KEY = os.getenv("SECRET_KEY")

FRONTEND_REGISTER_URL = 'www.kennerliga.de/#/register'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
    }
}
