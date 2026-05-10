"""ASGI config for Offside CRM. Available for future async server use."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "offside_crm.settings.prod")

application = get_asgi_application()
