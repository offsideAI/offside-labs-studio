from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.automations"
    label = "automations"

    def ready(self) -> None:  # type: ignore[override]
        # Importing the actions module registers the built-in handlers.
        from . import actions  # noqa: F401
