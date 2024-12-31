from datetime import datetime

import requests

from .utils import calculate_distance


def fetch_earthquakes(
    start_date: datetime.date,
    end_date: datetime.date,
    min_magnitude: float = 5.0,
    orderby: str = "time",
) -> dict:
    """
    Fetches earthquake data from the USGS API within a specified date range and minimum magnitude.

    This function sends a GET request to the USGS endpoint and retrieves a GeoJSON response
    containing earthquake data. It raises an HTTPError if the request fails.

    Args:
        start_date (date): The start date of the search range.
        end_date (date): The end date of the search range.
        min_magnitude (float, optional): The minimum magnitude of earthquakes to retrieve.
            Defaults to 5.0.
        orderby (str, optional): The ordering of results by time, magnitude, etc. Defaults to 'time'.

    Returns:
        dict: A dictionary (GeoJSON format) representing earthquake data.
    """
    USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson"
    params = {
        "starttime": start_date.isoformat(),
        "endtime": end_date.isoformat(),
        "minmagnitude": min_magnitude,
        "orderby": orderby,
        "format": "geojson",
    }
    response = requests.get(USGS_URL, params=params)
    response.raise_for_status()
    return response.json()


def find_nearest_earthquake(city_lat: float, city_lon: float, earthquakes: dict) -> dict:
    """
    Finds the nearest earthquake to a given city from a list of earthquake features.

    Iterates through the earthquake features returned by the USGS API response, calculates
    the distance of each to the given city coordinates, and selects the one with the minimum distance.

    Args:
        city_lat (float): The latitude of the city.
        city_lon (float): The longitude of the city.
        earthquakes (dict): The dictionary of earthquake data (GeoJSON), must contain 'features'.

    Returns:
        dict: The nearest earthquake feature dictionary. Returns None if no earthquakes are found.
    """
    if not earthquakes or "features" not in earthquakes:
        return None
    features = earthquakes["features"]
    if not features:
        return None

    min_dist = float("inf")
    nearest = None
    for feature in features:
        coords = feature["geometry"]["coordinates"]  # [lon, lat, depth]
        eq_lon, eq_lat = coords[0], coords[1]
        dist = calculate_distance(city_lat, city_lon, eq_lat, eq_lon)
        if dist < min_dist:
            min_dist = dist
            nearest = feature

    return nearest
