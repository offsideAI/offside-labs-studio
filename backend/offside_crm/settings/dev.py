"""Dev settings — extends base with debug toolbar + browser reload."""

from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE = [
    MIDDLEWARE[0],
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    *MIDDLEWARE[1:],
]

INTERNAL_IPS = ["127.0.0.1"]
