# Airfacts Database Schema

This document describes the Neo4j graph database schema used in the Airfacts project.

## Overview

The Airfacts database is a graph database built with Neo4j that models the relationships between airports, airlines, and flight routes. The schema is designed to efficiently query aviation data including route planning, network analysis, and geographic information.

## Data Source

All data is sourced from [OpenFlights](https://openflights.org/data.html), an open-source database of flight-related information.

## Node Types

### 1. Airport Node

Represents a physical airport location.

**Label:** `Airport`

**Properties:**

| Property                | Type    | Description                             | Example                                | Required |
| ----------------------- | ------- | --------------------------------------- | -------------------------------------- | -------- |
| `AirportID`             | Integer | Unique OpenFlights identifier           | 3797                                   | Yes      |
| `Name`                  | String  | Full airport name                       | "John F Kennedy International Airport" | Yes      |
| `City`                  | String  | City where airport is located           | "New York"                             | Yes      |
| `Country`               | String  | Country where airport is located        | "United States"                        | Yes      |
| `IATA`                  | String  | 3-letter IATA code (unique identifier)  | "JFK"                                  | Yes\*    |
| `ICAO`                  | String  | 4-letter ICAO code                      | "KJFK"                                 | No       |
| `Latitude`              | Float   | Geographic latitude in decimal degrees  | 40.639751                              | Yes      |
| `Longitude`             | Float   | Geographic longitude in decimal degrees | -73.778925                             | Yes      |
| `Altitude`              | Integer | Elevation above sea level in feet       | 13                                     | No       |
| `Timezone`              | Float   | Hours offset from UTC                   | -5.0                                   | No       |
| `DST`                   | String  | Daylight savings time zone              | "A"                                    | No       |
| `Tz database time zone` | String  | Timezone identifier                     | "America/New_York"                     | No       |
| `Type`                  | String  | Type of airport                         | "airport"                              | No       |
| `Source`                | String  | Data source                             | "OurAirports"                          | No       |

**Notes:**

- `IATA` is the primary unique identifier used for lookups
- Some airports may not have IATA codes (marked as "\\N" in source data)
- Coordinates are essential for distance calculations

**Indexes:**

```cypher
CREATE INDEX airport_iata IF NOT EXISTS FOR (a:Airport) ON (a.IATA);
CREATE INDEX airport_country IF NOT EXISTS FOR (a:Airport) ON (a.Country);
CREATE INDEX airport_name IF NOT EXISTS FOR (a:Airport) ON (a.Name);
```

**Example:**

```cypher
{
  AirportID: 3797,
  Name: "John F Kennedy International Airport",
  City: "New York",
  Country: "United States",
  IATA: "JFK",
  ICAO: "KJFK",
  Latitude: 40.639751,
  Longitude: -73.778925,
  Altitude: 13,
  Timezone: -5.0,
  DST: "A",
  "Tz database time zone": "America/New_York",
  Type: "airport",
  Source: "OurAirports"
}
```

### 2. Airline Node

Represents an airline company that operates flights.

**Label:** `Airline`

**Properties:**

| Property    | Type    | Description                            | Example             | Required |
| ----------- | ------- | -------------------------------------- | ------------------- | -------- |
| `AirlineID` | Integer | Unique OpenFlights identifier          | 24                  | Yes      |
| `Name`      | String  | Full airline name                      | "American Airlines" | Yes      |
| `Alias`     | String  | Airline alias or alternative name      | "\\N"               | No       |
| `IATA`      | String  | 2-letter IATA code (unique identifier) | "AA"                | Yes\*    |
| `ICAO`      | String  | 3-letter ICAO code                     | "AAL"               | No       |
| `Callsign`  | String  | Airline call sign for ATC              | "AMERICAN"          | No       |
| `Country`   | String  | Country where airline is based         | "United States"     | Yes      |
| `Active`    | String  | Whether airline is currently active    | "Y" or "N"          | Yes      |

**Notes:**

- `IATA` is the primary unique identifier (2 letters for airlines vs 3 for airports)
- `Active` indicates operational status ("Y" = active, "N" = inactive)
- Some airlines may not have IATA codes

**Indexes:**

```cypher
CREATE INDEX airline_iata IF NOT EXISTS FOR (a:Airline) ON (a.IATA);
CREATE INDEX airline_country IF NOT EXISTS FOR (a:Airline) ON (a.Country);
CREATE INDEX airline_name IF NOT EXISTS FOR (a:Airline) ON (a.Name);
```

**Example:**

```cypher
{
  AirlineID: 24,
  Name: "American Airlines",
  Alias: "\\N",
  IATA: "AA",
  ICAO: "AAL",
  Callsign: "AMERICAN",
  Country: "United States",
  Active: "Y"
}
```

## Relationship Types

### ROUTE Relationship

Represents a flight route from one airport to another operated by a specific airline.

**Type:** `ROUTE`

**Direction:** Directed (source airport → destination airport)

**Properties:**

| Property    | Type    | Description                    | Example     | Required |
| ----------- | ------- | ------------------------------ | ----------- | -------- |
| `Airline`   | String  | IATA code of operating airline | "AA"        | Yes      |
| `Codeshare` | String  | Whether route is a codeshare   | "Y" or null | No       |
| `Stops`     | Integer | Number of stops (0 = direct)   | 0           | Yes      |
| `Equipment` | String  | Aircraft type(s) used          | "738 319"   | No       |
| `Distance`  | Float   | Route distance in kilometers   | 3974.34     | No\*\*   |

**Notes:**

- `Airline` links the route to an airline (stores IATA code)
- `Stops` = 0 indicates a direct flight
- `Equipment` may contain multiple aircraft types separated by spaces
- `Distance` is calculated using Haversine formula (not in original OpenFlights data)

**Pattern:**

```cypher
(source:Airport)-[r:ROUTE]->(destination:Airport)
```

**Example:**

```cypher
(JFK:Airport)-[r:ROUTE {
  Airline: "AA",
  Codeshare: null,
  Stops: 0,
  Equipment: "738",
  Distance: 3974.34
}]->(LAX:Airport)
```

## Graph Patterns

### Common Query Patterns

#### 1. Find Direct Routes Between Airports

```cypher
MATCH (source:Airport {IATA: 'JFK'})-[r:ROUTE]->(dest:Airport {IATA: 'LAX'})
RETURN source, r, dest
```

#### 2. Find All Routes from an Airport

```cypher
MATCH (source:Airport {IATA: 'JFK'})-[r:ROUTE]->(dest:Airport)
RETURN source.IATA as from, dest.IATA as to, r.Airline as airline, r.Distance as distance
ORDER BY r.Distance
```

#### 3. Find Routes Operated by an Airline

```cypher
MATCH (source:Airport)-[r:ROUTE {Airline: 'AA'}]->(dest:Airport)
RETURN source.IATA as from, dest.IATA as to, r.Distance as distance
LIMIT 100
```

#### 4. Find Airports in a Country

```cypher
MATCH (a:Airport {Country: 'United States'})
RETURN a.IATA, a.Name, a.City
ORDER BY a.Name
```

#### 5. Find Airlines Operating in a Country

```cypher
MATCH (a:Airline {Country: 'United States'})
WHERE a.Active = 'Y'
RETURN a.IATA, a.Name
ORDER BY a.Name
```

#### 6. Network Analysis - Top Hub Airports

```cypher
MATCH (a:Airport)-[r:ROUTE]->()
RETURN a.IATA, a.Name, a.City, a.Country, count(r) as route_count
ORDER BY route_count DESC
LIMIT 20
```

#### 7. Find Routes with Specific Number of Stops

```cypher
MATCH (source:Airport)-[r:ROUTE {Stops: 0}]->(dest:Airport)
WHERE r.Airline = 'AA'
RETURN source.IATA, dest.IATA, r.Distance
```

#### 8. Calculate Distance Between Airports (if not stored)

```cypher
// Note: Use the helper.distance module in Python instead
MATCH (source:Airport {IATA: 'JFK'}), (dest:Airport {IATA: 'LAX'})
RETURN source.Latitude, source.Longitude, dest.Latitude, dest.Longitude
```

## Database Statistics

To get overview statistics about the database:

```cypher
// Count all airports
MATCH (a:Airport) RETURN count(a) as total_airports;

// Count all airlines
MATCH (a:Airline) RETURN count(a) as total_airlines;

// Count all routes
MATCH ()-[r:ROUTE]->() RETURN count(r) as total_routes;

// Count active airlines
MATCH (a:Airline {Active: 'Y'}) RETURN count(a) as active_airlines;

// Count countries with airports
MATCH (a:Airport) RETURN count(DISTINCT a.Country) as countries;

// Average routes per airport
MATCH (a:Airport)-[r:ROUTE]->()
WITH a, count(r) as routes
RETURN avg(routes) as avg_routes_per_airport;
```

## Data Loading

### Load Order

1. **Load Airports** (nodes must exist before relationships)
2. **Load Airlines** (nodes must exist before relationships)
3. **Load Routes** (creates relationships between existing nodes)
4. **Calculate Distances** (optional: update ROUTE relationships with distances)

### Load Scripts

Located in `database/cypher/`:

- `load_airport.cypher` - Load airport nodes
- `load_airline.cypher` - Load airline nodes
- `load_route.cypher` - Load route relationships

Main loader: `database/loader.py`

## Constraints and Validations

### Uniqueness Constraints

```cypher
// Ensure IATA codes are unique
CREATE CONSTRAINT airport_iata_unique IF NOT EXISTS
FOR (a:Airport) REQUIRE a.IATA IS UNIQUE;

CREATE CONSTRAINT airline_iata_unique IF NOT EXISTS
FOR (a:Airline) REQUIRE a.IATA IS UNIQUE;
```

### Data Validation Rules

1. **Airport IATA Codes:**

   - Must be 3 characters (when present)
   - May be "\\N" for airports without IATA codes
   - Used as primary identifier

2. **Airline IATA Codes:**

   - Must be 2 characters (when present)
   - May be "\\N" for airlines without IATA codes
   - Used as primary identifier

3. **Coordinates:**

   - Latitude: -90 to 90
   - Longitude: -180 to 180
   - Required for distance calculations

4. **Route Stops:**
   - Must be non-negative integer
   - 0 = direct flight
   - 1+ = number of intermediate stops

## Distance Calculations

Routes in the original OpenFlights dataset do not include distance information. Distances can be calculated using the Haversine formula with airport coordinates.

### Using the Helper Module

```python
from database.helper import calculate_distance_km

# Calculate distance between two airports
distance = calculate_distance_km(
    source_lat, source_lon,
    dest_lat, dest_lon
)
```

### Updating Routes with Distances

```cypher
// Update a specific route with calculated distance
MATCH (source:Airport {IATA: 'JFK'})-[r:ROUTE]->(dest:Airport {IATA: 'LAX'})
SET r.Distance = 3974.34
RETURN r.Distance;

// Find routes without distances
MATCH (source:Airport)-[r:ROUTE]->(dest:Airport)
WHERE r.Distance IS NULL
  AND source.Latitude IS NOT NULL
  AND dest.Latitude IS NOT NULL
RETURN count(r) as routes_without_distance;
```

## Performance Considerations

### Indexes

Critical indexes for query performance:

- `Airport.IATA` - Most airport lookups use IATA code
- `Airline.IATA` - Most airline lookups use IATA code
- `Airport.Country` - Country-based filtering
- `Airline.Country` - Country-based filtering

### Query Optimization Tips

1. **Use IATA codes** for lookups instead of names (indexed)
2. **Limit results** when exploring data to avoid large result sets
3. **Use parameters** in queries for prepared statement benefits
4. **Filter early** in MATCH clauses to reduce intermediate results
5. **Specify direction** in route queries when possible

## Schema Version

**Version:** 1.0  
**Last Updated:** November 2025  
**Neo4j Version Compatibility:** 4.0+

## Migration Notes

If updating from OpenFlights data:

1. Airport and Airline IDs may change between data dumps
2. IATA codes are stable identifiers
3. Always use IATA for cross-version compatibility
4. Distance property is custom addition (not in original data)

## References

- [OpenFlights Airport Database](https://openflights.org/data.html#airport)
- [OpenFlights Airline Database](https://openflights.org/data.html#airline)
- [OpenFlights Route Database](https://openflights.org/data.html#route)
- [IATA Airport Codes](https://www.iata.org/en/publications/directories/code-search/)
- [ICAO Location Indicators](https://www.icao.int/publications/DOC7910/Pages/default.aspx)
