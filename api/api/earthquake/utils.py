from decimal import Decimal
from math import atan2, cos, radians, sin, sqrt
from typing import Union


def calculate_distance(
    lat1: Union[Decimal, float],
    lon1: Union[Decimal, float],
    lat2: Union[Decimal, float],
    lon2: Union[Decimal, float],
) -> float:
    """
    Calculates the great-circle distance between two points on Earth using the Haversine formula.

    Args:
        lat1 (Decimal or float): The latitude of the first point.
        lon1 (Decimal or float): The longitude of the first point.
        lat2 (Decimal or float): The latitude of the second point.
        lon2 (Decimal or float): The longitude of the second point.

    Returns:
        float: The distance in kilometers between the two given points.
    """
    # Convert Decimal to float if necessary
    lat1_f: float = float(lat1)
    lon1_f: float = float(lon1)
    lat2_f: float = float(lat2)
    lon2_f: float = float(lon2)

    earth_radius: float = 6371.0  # Earth radius in km
    dlat: float = radians(lat2_f - lat1_f)
    dlon: float = radians(lon2_f - lon1_f)

    a: float = sin(dlat / 2) ** 2 + cos(radians(lat1_f)) * cos(radians(lat2_f)) * sin(dlon / 2) ** 2
    c: float = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance: float = earth_radius * c
    return distance
