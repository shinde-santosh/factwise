from ..base import *

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-local-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

IS_LOCAL = True
