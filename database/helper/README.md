# Database Helper Functions

This module provides utility functions for database operations, particularly for calculating distances between geographic coordinates.

## Distance Calculation

The distance calculation functions use the **Haversine formula** to calculate the great-circle distance between two points on Earth given their latitude and longitude coordinates.

### Functions

#### `calculate_distance(lat1, lon1, lat2, lon2, unit='km')`

Calculate the distance between two geographic coordinates.

**Parameters:**

- `lat1` (float): Latitude of the first point in decimal degrees
- `lon1` (float): Longitude of the first point in decimal degrees
- `lat2` (float): Latitude of the second point in decimal degrees
- `lon2` (float): Longitude of the second point in decimal degrees
- `unit` (str): Unit of measurement - 'km' (kilometers), 'mi' (miles), or 'nm' (nautical miles)

**Returns:**

- `float`: Distance between the two points in the specified unit

**Example:**

```python
from database.helper import calculate_distance

# Distance from New York (JFK) to Los Angeles (LAX)
distance = calculate_distance(40.6413, -73.7781, 33.9416, -118.4085)
print(f"{distance:.2f} km")  # Output: 3974.34 km
```

#### `calculate_distance_km(lat1, lon1, lat2, lon2)`

Convenience function to calculate distance in kilometers.

**Example:**

```python
from database.helper import calculate_distance_km

# Distance from London (LHR) to Paris (CDG)
distance = calculate_distance_km(51.4700, -0.4543, 49.0097, 2.5479)
print(f"{distance:.2f} km")  # Output: 346.96 km
```

#### `calculate_distance_miles(lat1, lon1, lat2, lon2)`

Convenience function to calculate distance in miles.

**Example:**

```python
from database.helper import calculate_distance_miles

# Distance from New York to Los Angeles
distance = calculate_distance_miles(40.6413, -73.7781, 33.9416, -118.4085)
print(f"{distance:.2f} miles")  # Output: 2469.57 miles
```

#### `get_distance_between_airports(origin_lat, origin_lon, dest_lat, dest_lon, round_to=2)`

Calculate distance between two airports with automatic rounding.

**Parameters:**

- `origin_lat` (float): Origin airport latitude
- `origin_lon` (float): Origin airport longitude
- `dest_lat` (float): Destination airport latitude
- `dest_lon` (float): Destination airport longitude
- `round_to` (int): Number of decimal places to round to (default: 2)

**Returns:**

- `float`: Distance in kilometers, rounded to specified decimal places

**Example:**

```python
from database.helper import get_distance_between_airports

dist = get_distance_between_airports(40.6413, -73.7781, 33.9416, -118.4085)
print(dist)  # Output: 3974.34
```

#### `validate_coordinates(lat, lon)`

Validate that latitude and longitude are within valid ranges.

**Parameters:**

- `lat` (float): Latitude in decimal degrees
- `lon` (float): Longitude in decimal degrees

**Returns:**

- `bool`: True if coordinates are valid, False otherwise

**Example:**

```python
from database.helper import validate_coordinates

is_valid = validate_coordinates(40, -73)
print(is_valid)  # Output: True

is_valid = validate_coordinates(100, -73)  # Invalid latitude
print(is_valid)  # Output: False
```

#### `calculate_distance_safe(lat1, lon1, lat2, lon2, unit='km')`

Calculate distance with validation and error handling. Returns `None` if any coordinate is None or invalid.

**Example:**

```python
from database.helper import calculate_distance_safe

# Will return None if coordinates are invalid or None
distance = calculate_distance_safe(None, None, 40, -73)
print(distance)  # Output: None

distance = calculate_distance_safe(40, -73, 41, -74)
print(f"{distance:.2f} km")  # Output: 127.39 km
```

## Usage in Database Operations

### Example: Calculate Route Distance

```python
from neo4j import GraphDatabase
from database.helper import get_distance_between_airports

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def add_distance_to_route(tx, source_iata, dest_iata):
    """Add distance to a route based on airport coordinates"""
    query = """
    MATCH (source:Airport {IATA: $source})-[r:ROUTE]->(dest:Airport {IATA: $dest})
    WHERE source.Latitude IS NOT NULL AND source.Longitude IS NOT NULL
      AND dest.Latitude IS NOT NULL AND dest.Longitude IS NOT NULL
    RETURN source.Latitude as src_lat, source.Longitude as src_lon,
           dest.Latitude as dest_lat, dest.Longitude as dest_lon
    """
    result = tx.run(query, source=source_iata, dest=dest_iata)
    record = result.single()

    if record:
        distance = get_distance_between_airports(
            record['src_lat'], record['src_lon'],
            record['dest_lat'], record['dest_lon']
        )

        # Update the route with calculated distance
        update_query = """
        MATCH (source:Airport {IATA: $source})-[r:ROUTE]->(dest:Airport {IATA: $dest})
        SET r.Distance = $distance
        """
        tx.run(update_query, source=source_iata, dest=dest_iata, distance=distance)
        return distance
    return None

with driver.session() as session:
    distance = session.execute_write(add_distance_to_route, "JFK", "LAX")
    print(f"Distance added: {distance} km")

driver.close()
```

### Example: Bulk Distance Calculation

```python
from database.helper import calculate_distance_km

def calculate_all_route_distances(tx):
    """Calculate and store distances for all routes"""
    query = """
    MATCH (source:Airport)-[r:ROUTE]->(dest:Airport)
    WHERE source.Latitude IS NOT NULL AND source.Longitude IS NOT NULL
      AND dest.Latitude IS NOT NULL AND dest.Longitude IS NOT NULL
      AND r.Distance IS NULL
    RETURN source.IATA as source, dest.IATA as dest,
           source.Latitude as src_lat, source.Longitude as src_lon,
           dest.Latitude as dest_lat, dest.Longitude as dest_lon
    LIMIT 1000
    """
    results = tx.run(query)

    for record in results:
        distance = calculate_distance_km(
            record['src_lat'], record['src_lon'],
            record['dest_lat'], record['dest_lon']
        )

        # Update route
        update_query = """
        MATCH (source:Airport {IATA: $source})-[r:ROUTE]->(dest:Airport {IATA: $dest})
        SET r.Distance = $distance
        """
        tx.run(update_query, source=record['source'], dest=record['dest'], distance=distance)
```

## Testing

Run the test suite:

```bash
cd database/helper
python test_distance.py
```

Or with pytest:

```bash
pytest test_distance.py -v
```

## Technical Details

### Haversine Formula

The Haversine formula is used to calculate the great-circle distance between two points on a sphere:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1−a))
d = R × c
```

Where:

- `lat1`, `lon1` = coordinates of first point
- `lat2`, `lon2` = coordinates of second point
- `Δlat` = lat2 - lat1
- `Δlon` = lon2 - lon1
- `R` = Earth's radius (6371 km, 3958.8 miles, or 3440.1 nautical miles)
- `d` = distance

### Accuracy

The Haversine formula assumes Earth is a perfect sphere, which provides accuracy within 0.5% for most distances. For higher precision calculations considering Earth's ellipsoidal shape, the Vincenty formula could be used instead.

### Earth's Radius Values

- **Kilometers**: 6371.0 km
- **Miles**: 3958.8 mi
- **Nautical Miles**: 3440.1 nm

## Known Limitations

1. Assumes Earth is a perfect sphere (not accounting for ellipsoidal shape)
2. Does not account for terrain or actual flight paths
3. Calculates great-circle distance (shortest path on a sphere)
4. Does not consider obstacles, airspace restrictions, or routing requirements

## References

- [Haversine Formula - Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
- [Great-circle distance - Wikipedia](https://en.wikipedia.org/wiki/Great-circle_distance)
- [OpenFlights Data](https://openflights.org/data.html)
