from decimal import Decimal

from django.db import models


class City(models.Model):
    """
    Represents a city with a name and geographic coordinates. Used to
    associate earthquake searches with a known location.

    Args:
        name (str): The unique name of the city.
        latitude (Decimal): The latitude coordinate of the city.
        longitude (Decimal): The longitude coordinate of the city.

    Attributes:
        name (str): The city name stored in the database.
        latitude (Decimal): The stored latitude of this city.
        longitude (Decimal): The stored longitude of this city.
        created_at (datetime): The timestamp indicating when this city entry was created.
    """

    name: str = models.CharField(max_length=255, unique=True)
    latitude: Decimal = models.DecimalField(max_digits=9, decimal_places=6)
    longitude: Decimal = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the City.

        Returns:
            str: The name of the city.
        """
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class EarthquakeSearchResult(models.Model):
    """
    Represents a cached search for earthquakes associated with a specific city and date range.
    Stores both raw earthquake data and the details of the nearest earthquake found.

    Args:
        city (City): The city object to which this search result is related.
        start_date (date): The start date of the search range.
        end_date (date): The end date of the search range.

    Attributes:
        city (City): The related city for this search.
        start_date (date): The start of the date range used in the search.
        end_date (date): The end of the date range used in the search.
        raw_earthquake_data (dict): The raw JSON data returned from the USGS API.
        nearest_earthquake_location (str): Location description of the nearest earthquake found.
        nearest_earthquake_magnitude (float): Magnitude of the nearest earthquake found.
        nearest_earthquake_time (datetime): Timestamp of the nearest earthquake event.
        created_at (datetime): When this search result was created.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    raw_earthquake_data = models.JSONField(default=dict, blank=True)
    nearest_earthquake_location = models.CharField(max_length=255, null=True, blank=True)
    nearest_earthquake_magnitude = models.FloatField(null=True, blank=True)
    nearest_earthquake_time = models.DateTimeField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def verbose_msg(self):
        try:
            msg = (
                f"Result for {self.city.name} between {self.start_date.strftime('%B %d %Y')} "
                f"and {self.end_date.strftime('%B %d %Y')}:"
                f" The closest earthquake to {self.city.name} was a "
                f"M {self.raw_earthquake_data['properties']['mag']} at {self.distance_km:.1f} km away, "
                f"{self.raw_earthquake_data['properties']['place']}, "
                f"on {self.nearest_earthquake_time.strftime('%B %d %Y at %H:%M')} UTC."
            )
        except KeyError:
            msg = "No results found"
        return msg

    class Meta:
        indexes = [
            models.Index(fields=["city", "start_date", "end_date"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the EarthquakeSearchResult.

        Returns:
            str: A descriptive string of the search result including city and date range.
        """
        return f"EarthquakeSearchResult for {self.city.name} ({self.start_date} to {self.end_date})"
