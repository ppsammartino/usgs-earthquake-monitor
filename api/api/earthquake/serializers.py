from rest_framework import serializers

from .models import City, EarthquakeSearchResult


class CitySerializer(serializers.ModelSerializer):
    """
    A serializer for the City model that converts City instances to and from various data
    formats (typically JSON) suitable for API endpoints.

    This serializer ensures that creating or retrieving a city is straightforward and
    structured, making it easy to integrate with the API views.

    Attributes:
        id (int): The unique identifier of the city.
        name (str): The city's name.
        latitude (float): The city's latitude.
        longitude (float): The city's longitude.
    """

    class Meta:
        model = City
        fields = ["id", "name", "latitude", "longitude"]


from datetime import date, datetime
from typing import Optional

from rest_framework import serializers


class NearestEarthquakeSerializer(serializers.Serializer):
    """
    Represents the details of the nearest earthquake found.

    Fields:
        location (str): A textual description of where the earthquake occurred.
        magnitude (float): The magnitude of the earthquake on the Richter scale.
        time (datetime): The UTC timestamp when the earthquake occurred.
    """

    location: str = serializers.CharField()
    magnitude: float = serializers.FloatField()
    time: datetime = serializers.DateTimeField()


class EarthquakeSearchSerializer(serializers.Serializer):
    """
    Represents the result of an earthquake search for a given city and date range.

    Fields:
        city (str): The name of the city for which the search was performed.
        start_date (date): The start date of the search range.
        end_date (date): The end date of the search range.
        nearest_earthquake (NearestEarthquakeSerializer, optional):
            The details of the closest earthquake, if any were found.
    """

    city: str = serializers.CharField()
    start_date: date = serializers.DateField()
    end_date: date = serializers.DateField()
    nearest_earthquake: Optional[NearestEarthquakeSerializer] = NearestEarthquakeSerializer(required=False)


class EarthquakeSearchResultSerializer(serializers.ModelSerializer):
    """
    Serializer for the EarthquakeSearchResult model to handle serialization
    and deserialization of the model data.
    """

    raw_earthquake_data = serializers.JSONField(write_only=True)
    city_name = serializers.ReadOnlyField(source="city.name")
    verbose_msg = serializers.ReadOnlyField()

    class Meta:
        model = EarthquakeSearchResult
        fields = "__all__"
