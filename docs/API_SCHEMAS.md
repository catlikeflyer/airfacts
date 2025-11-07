# API Schemas Documentation

This document describes the data schemas used in the Airfacts API.

## Overview

The API uses Pydantic models for data validation and serialization. All schemas are defined in `api/schemas.py`.

## Airport Schemas

### AirportBase

Basic airport information returned by list endpoints.

**Fields:**

- `IATA` (string, required): IATA code of the airport (e.g., "JFK")
- `Name` (string, required): Full name of the airport (e.g., "John F Kennedy International Airport")
- `City` (string, required): City where the airport is located (e.g., "New York")
- `Country` (string, required): Country where the airport is located (e.g., "United States")

**Used in:**

- `GET /api/airports/` - Get all airports
- `GET /api/airports/country/{country}` - Get airports by country

### AirportDetail

Extended airport information with all available fields.

**Fields (extends AirportBase):**

- All fields from `AirportBase`
- `ICAO` (string, optional): ICAO code (e.g., "KJFK")
- `Latitude` (float, optional): Latitude coordinate (e.g., 40.639751)
- `Longitude` (float, optional): Longitude coordinate (e.g., -73.778925)
- `Altitude` (integer, optional): Altitude in feet (e.g., 13)
- `Timezone` (string, optional): Hours offset from UTC (e.g., "-5")
- `DST` (string, optional): Daylight savings time zone (e.g., "A")
- `TzDatabaseTimeZone` (string, optional): Timezone in Olson format (e.g., "America/New_York")
- `Type` (string, optional): Type of airport (e.g., "airport")
- `Source` (string, optional): Data source (e.g., "OurAirports")

**Used in:**

- `GET /api/airports/{iata}` - Get airport by IATA code

---

## Airline Schemas

### AirlineBase

Basic airline information returned by list endpoints.

**Fields:**

- `IATA` (string, required): IATA code of the airline (e.g., "AA")
- `Name` (string, required): Name of the airline (e.g., "American Airlines")
- `Country` (string, required): Country where the airline is based (e.g., "United States")

**Used in:**

- `GET /api/airlines/` - Get all airlines
- `GET /api/airlines/country/{country}` - Get airlines by country

### AirlineDetail

Extended airline information with all available fields.

**Fields (extends AirlineBase):**

- All fields from `AirlineBase`
- `ICAO` (string, optional): ICAO code (e.g., "AAL")
- `Callsign` (string, optional): Airline callsign (e.g., "AMERICAN")
- `Alias` (string, optional): Airline alias
- `Active` (string, optional): "Y" if active, "N" if inactive (e.g., "Y")

**Used in:**

- `GET /api/airlines/{iata}` - Get airline by IATA code

---

## Route Schemas

### RouteBase

Route information showing flight connections between airports.

**Fields:**

- `source` (string, required): IATA code of source airport (e.g., "JFK")
- `destination` (string, required): IATA code of destination airport (e.g., "LAX")
- `airline` (string, required): IATA code of operating airline (e.g., "AA")
- `distance` (float, optional): Distance in kilometers (e.g., 3983.0)

**Used in:**

- `GET /api/routes/source/{source_iata}` - Get routes from source airport
- `GET /api/routes/destination/{destination_iata}` - Get routes to destination
- `GET /api/routes/source/{source_iata}/destination/{destination_iata}` - Get routes between airports
- `GET /api/routes/airline/{airline_iata}` - Get routes by airline

### RouteDetail

Extended route information (for future use).

**Fields (extends RouteBase):**

- All fields from `RouteBase`
- `stops` (integer, optional): Number of stops (0 for direct) (e.g., 0)
- `equipment` (string, optional): Aircraft types used (e.g., "737 738 739")
- `codeshare` (string, optional): Codeshare indicator

---

## Utility Schemas

### ErrorResponse

Standard error response format.

**Fields:**

- `detail` (string, required): Error message (e.g., "Airport not found")

**Used in:**

- All endpoints for 404 and error responses

### PaginationParams

Pagination parameters (currently defined but not used in all endpoints).

**Fields:**

- `limit` (integer, default=50, min=1, max=1000): Maximum items to return
- `skip` (integer, default=0, min=0): Number of items to skip

---

## Example Responses

### Airport Example (Detail)

```json
{
  "IATA": "JFK",
  "Name": "John F Kennedy International Airport",
  "City": "New York",
  "Country": "United States",
  "ICAO": "KJFK",
  "Latitude": 40.639751,
  "Longitude": -73.778925,
  "Altitude": 13,
  "Timezone": "-5",
  "DST": "A",
  "Tz database time zone": "America/New_York",
  "Type": "airport",
  "Source": "OurAirports"
}
```

### Airline Example (Detail)

```json
{
  "IATA": "AA",
  "Name": "American Airlines",
  "Country": "United States",
  "ICAO": "AAL",
  "Callsign": "AMERICAN",
  "Alias": null,
  "Active": "Y"
}
```

### Route Example

```json
{
  "source": "JFK",
  "destination": "LAX",
  "airline": "AA",
  "distance": 3983.0
}
```

### Error Example

```json
{
  "detail": "Airport not found"
}
```

---

## Data Source

All data is fetched from [OpenFlights](https://openflights.org/data.html) which provides comprehensive aviation data including airports, airlines, and routes worldwide.

## Notes

- All IATA/ICAO codes are automatically converted to uppercase by the API
- Optional fields may be `null` if data is not available
- Distance calculations are in kilometers
- The API uses FastAPI's automatic OpenAPI documentation available at `/docs` when running the server
