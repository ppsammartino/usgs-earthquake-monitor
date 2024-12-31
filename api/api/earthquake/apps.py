from django.apps import AppConfig


class EarthquakeConfig(AppConfig):
    """
    App config for the Earthquake app, which handles storing city data,
    querying earthquakes, and returning nearest earthquake results.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api.earthquake"
