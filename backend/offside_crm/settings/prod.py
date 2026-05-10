"""Production settings — extends base with HTTPS hardening."""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

# --- Security ---

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://app.offside.ai,https://crm-api.offside.ai,https://platform.offside.ai",
    ).split(",")
]
