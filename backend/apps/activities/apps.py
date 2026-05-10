from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.activities"
    label = "activities"

    def ready(self) -> None:  # type: ignore[override]
        # Register Django signals once Django is set up.
        from . import signals  # noqa: F401
