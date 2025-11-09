"""
Distance calculation utilities using the Haversine formula.

The Haversine formula calculates the great-circle distance between two points
on a sphere given their longitudes and latitudes.
"""

import math
from typing import Tuple, Optional


def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "km"
) -> float:
    """
    Calculate the distance between two geographic coordinates.

    Uses the Haversine formula to calculate the great-circle distance between
    two points on Earth specified by latitude and longitude.

    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees
        unit: Unit of measurement ('km' for kilometers, 'mi' for miles, 'nm' for nautical miles)

    Returns:
        Distance between the two points in the specified unit

    Example:
        >>> # Distance from New York (JFK) to Los Angeles (LAX)
        >>> distance = calculate_distance(40.6413, -73.7781, 33.9416, -118.4085)
        >>> print(f"{distance:.2f} km")
        3983.35 km
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in kilometers
    earth_radius_km = 6371.0

    # Calculate distance based on unit
    if unit.lower() == "km":
        return c * earth_radius_km
    elif unit.lower() in ["mi", "miles"]:
        earth_radius_miles = 3958.8
        return c * earth_radius_miles
    elif unit.lower() in ["nm", "nautical"]:
        earth_radius_nm = 3440.1
        return c * earth_radius_nm
    else:
        raise ValueError(
            f"Invalid unit '{unit}'. Use 'km', 'mi' (miles), or 'nm' (nautical miles)"
        )


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two geographic coordinates in kilometers.

    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees

    Returns:
        Distance between the two points in kilometers

    Example:
        >>> # Distance from London (LHR) to Paris (CDG)
        >>> distance = calculate_distance_km(51.4700, -0.4543, 49.0097, 2.5479)
        >>> print(f"{distance:.2f} km")
        344.37 km
    """
    return calculate_distance(lat1, lon1, lat2, lon2, unit="km")


def calculate_distance_miles(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the distance between two geographic coordinates in miles.

    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees

    Returns:
        Distance between the two points in miles

    Example:
        >>> # Distance from New York (JFK) to London (LHR)
        >>> distance = calculate_distance_miles(40.6413, -73.7781, 51.4700, -0.4543)
        >>> print(f"{distance:.2f} miles")
        3451.52 miles
    """
    return calculate_distance(lat1, lon1, lat2, lon2, unit="mi")


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate that latitude and longitude are within valid ranges.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        True if coordinates are valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def calculate_distance_safe(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
    unit: str = "km",
) -> Optional[float]:
    """
    Calculate distance with validation and error handling.

    Returns None if any coordinate is None or invalid.

    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees
        unit: Unit of measurement ('km', 'mi', or 'nm')

    Returns:
        Distance in specified unit, or None if coordinates are invalid
    """
    # Check for None values
    if None in [lat1, lon1, lat2, lon2]:
        return None

    # Validate coordinates
    if not (validate_coordinates(lat1, lon1) and validate_coordinates(lat2, lon2)):
        return None

    try:
        return calculate_distance(lat1, lon1, lat2, lon2, unit)
    except Exception:
        return None


# Convenience function for database queries
def get_distance_between_airports(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    round_to: int = 2,
) -> float:
    """
    Calculate distance between two airports and round the result.

    This function is optimized for use in database operations where
    you need consistent, rounded distance values.

    Args:
        origin_lat: Origin airport latitude
        origin_lon: Origin airport longitude
        dest_lat: Destination airport latitude
        dest_lon: Destination airport longitude
        round_to: Number of decimal places to round to (default: 2)

    Returns:
        Distance in kilometers, rounded to specified decimal places

    Example:
        >>> dist = get_distance_between_airports(40.6413, -73.7781, 33.9416, -118.4085)
        >>> print(dist)
        3983.35
    """
    distance = calculate_distance_km(origin_lat, origin_lon, dest_lat, dest_lon)
    return round(distance, round_to)
