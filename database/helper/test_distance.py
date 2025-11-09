"""
Unit tests for distance calculation functions.
Run with: python -m pytest test_distance.py
or: python test_distance.py
"""

import unittest
import math
from distance import (
    calculate_distance,
    calculate_distance_km,
    calculate_distance_miles,
    validate_coordinates,
    calculate_distance_safe,
    get_distance_between_airports,
)


class TestDistanceCalculations(unittest.TestCase):
    """Test suite for distance calculation functions"""

    def test_calculate_distance_km(self):
        """Test distance calculation in kilometers"""
        # JFK to LAX
        jfk_lat, jfk_lon = 40.6413, -73.7781
        lax_lat, lax_lon = 33.9416, -118.4085

        distance = calculate_distance_km(jfk_lat, jfk_lon, lax_lat, lax_lon)

        # Expected distance is approximately 3974 km
        self.assertAlmostEqual(distance, 3974, delta=10)

    def test_calculate_distance_miles(self):
        """Test distance calculation in miles"""
        # JFK to LAX
        jfk_lat, jfk_lon = 40.6413, -73.7781
        lax_lat, lax_lon = 33.9416, -118.4085

        distance = calculate_distance_miles(jfk_lat, jfk_lon, lax_lat, lax_lon)

        # Expected distance is approximately 2469 miles
        self.assertAlmostEqual(distance, 2469, delta=10)

    def test_calculate_distance_with_unit(self):
        """Test distance calculation with different units"""
        lat1, lon1 = 51.4700, -0.4543  # London
        lat2, lon2 = 49.0097, 2.5479  # Paris

        dist_km = calculate_distance(lat1, lon1, lat2, lon2, unit="km")
        dist_mi = calculate_distance(lat1, lon1, lat2, lon2, unit="mi")
        dist_nm = calculate_distance(lat1, lon1, lat2, lon2, unit="nm")

        # Check that conversions are approximately correct
        self.assertAlmostEqual(dist_km, dist_mi * 1.60934, delta=5)
        self.assertAlmostEqual(dist_km, dist_nm * 1.852, delta=5)

    def test_invalid_unit(self):
        """Test that invalid unit raises ValueError"""
        with self.assertRaises(ValueError):
            calculate_distance(0, 0, 1, 1, unit="invalid")

    def test_same_location(self):
        """Test distance between same location is zero"""
        distance = calculate_distance_km(40.0, -74.0, 40.0, -74.0)
        self.assertAlmostEqual(distance, 0, places=2)

    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid coordinates"""
        self.assertTrue(validate_coordinates(0, 0))
        self.assertTrue(validate_coordinates(90, 180))
        self.assertTrue(validate_coordinates(-90, -180))
        self.assertTrue(validate_coordinates(45.5, -122.6))

    def test_validate_coordinates_invalid(self):
        """Test coordinate validation with invalid coordinates"""
        self.assertFalse(validate_coordinates(91, 0))  # Latitude too high
        self.assertFalse(validate_coordinates(-91, 0))  # Latitude too low
        self.assertFalse(validate_coordinates(0, 181))  # Longitude too high
        self.assertFalse(validate_coordinates(0, -181))  # Longitude too low

    def test_calculate_distance_safe_with_none(self):
        """Test safe calculation with None values"""
        result = calculate_distance_safe(None, 0, 0, 0)
        self.assertIsNone(result)

        result = calculate_distance_safe(0, None, 0, 0)
        self.assertIsNone(result)

        result = calculate_distance_safe(0, 0, None, 0)
        self.assertIsNone(result)

        result = calculate_distance_safe(0, 0, 0, None)
        self.assertIsNone(result)

    def test_calculate_distance_safe_with_invalid(self):
        """Test safe calculation with invalid coordinates"""
        result = calculate_distance_safe(100, 0, 0, 0)  # Invalid latitude
        self.assertIsNone(result)

        result = calculate_distance_safe(0, 200, 0, 0)  # Invalid longitude
        self.assertIsNone(result)

    def test_calculate_distance_safe_with_valid(self):
        """Test safe calculation with valid coordinates"""
        result = calculate_distance_safe(40.0, -74.0, 41.0, -73.0)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_get_distance_between_airports(self):
        """Test airport distance calculation with rounding"""
        # JFK to LAX
        distance = get_distance_between_airports(40.6413, -73.7781, 33.9416, -118.4085)

        # Should be rounded to 2 decimal places
        self.assertIsInstance(distance, float)
        self.assertEqual(distance, round(distance, 2))

    def test_get_distance_between_airports_custom_rounding(self):
        """Test airport distance calculation with custom rounding"""
        distance = get_distance_between_airports(
            40.6413, -73.7781, 33.9416, -118.4085, round_to=0
        )

        # Should be rounded to integer
        self.assertIsInstance(distance, float)
        self.assertEqual(distance, round(distance, 0))

    def test_known_distances(self):
        """Test against known real-world distances"""
        # New York to London (approximately 5570 km)
        nyc_lat, nyc_lon = 40.7128, -74.0060
        lon_lat, lon_lon = 51.5074, -0.1278

        distance = calculate_distance_km(nyc_lat, nyc_lon, lon_lat, lon_lon)
        self.assertAlmostEqual(distance, 5570, delta=50)

        # Sydney to Singapore (approximately 6300 km)
        syd_lat, syd_lon = -33.8688, 151.2093
        sin_lat, sin_lon = 1.3521, 103.8198

        distance = calculate_distance_km(syd_lat, syd_lon, sin_lat, sin_lon)
        self.assertAlmostEqual(distance, 6300, delta=50)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases for distance calculations"""

    def test_antipodal_points(self):
        """Test distance between antipodal points (opposite sides of Earth)"""
        # Should be approximately half Earth's circumference (20,000 km)
        distance = calculate_distance_km(0, 0, 0, 180)
        self.assertAlmostEqual(distance, 20015, delta=50)

    def test_north_south_pole(self):
        """Test distance between North and South poles"""
        # Should be approximately half Earth's circumference
        distance = calculate_distance_km(90, 0, -90, 0)
        self.assertAlmostEqual(distance, 20015, delta=50)

    def test_crossing_date_line(self):
        """Test distance calculation crossing the international date line"""
        # Tokyo to San Francisco
        tokyo_lat, tokyo_lon = 35.6762, 139.6503
        sf_lat, sf_lon = 37.7749, -122.4194

        distance = calculate_distance_km(tokyo_lat, tokyo_lon, sf_lat, sf_lon)
        # Expected approximately 8280 km
        self.assertAlmostEqual(distance, 8280, delta=100)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
