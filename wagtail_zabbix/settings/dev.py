import os

from . import base as base_settings

globals().update(
    {
        name: getattr(base_settings, name)
        for name in dir(base_settings)
        if name.isupper()
    }
)
del base_settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

