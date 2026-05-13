"""Dev settings — extends base with debug toolbar + browser reload.

`debug_toolbar` and `django_browser_reload` live in requirements-dev.txt
(not requirements.txt), and the Dockerfile only installs
requirements.txt. So inside the docker-compose stack these modules are
not importable — we detect that and skip wiring them up. Local venvs
with `requirements-dev.txt` installed get the full dev experience.
"""

import importlib.util

from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True


def _is_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


_extra_apps: list[str] = []
_extra_middleware_after_security: list[str] = []

if _is_installed("debug_toolbar"):
    _extra_apps.append("debug_toolbar")
    _extra_middleware_after_security.append(
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    )

if _is_installed("django_browser_reload"):
    _extra_apps.append("django_browser_reload")
    _extra_middleware_after_security.append(
        "django_browser_reload.middleware.BrowserReloadMiddleware"
    )

INSTALLED_APPS = [*INSTALLED_APPS, *_extra_apps]

MIDDLEWARE = [
    MIDDLEWARE[0],
    *_extra_middleware_after_security,
    *MIDDLEWARE[1:],
]

INTERNAL_IPS = ["127.0.0.1"]
