"""WSGI config for Offside CRM. Used by gunicorn in production."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "offside_crm.settings.prod")

application = get_wsgi_application()
