# Airfacts API
This is a simple API that allows you to retrieve information about airports and airlines.

## Database installation
The project uses a Neo4j database. To run the database, you need to have Docker installed. To run the database, run the following command:

### Option 1. 
```bash
docker run --name neo4j -p 7474:7474 -p 7687:7687 -d -v $HOME/neo4j/data:/data -v $HOME/neo4j/logs:/logs -v $HOME/neo4j/import:/var/lib/neo4j/import -v $HOME/neo4j/plugins:/plugins --env NEO4J_AUTH=neo4j/airfacts neo4j:4.2
```

This will create a new container with the name `neo4j`. The database will be available at `http://localhost:7474`. The default username and password are `neo4j` and `airfacts-pw`.

### Option 2.
Alternatively, you can just create a local database within the Neo4j Desktop application. The database should be available at `http://localhost:7687`. Set the default username and password to `neo4j` and `airfacts-pw` as per the settings of this project.

## Database
The data itself comes from [Ahmads Rafiee's](https://www.kaggle.com/datasets/ahmadrafiee/airports-airlines-planes-and-routes-update-2024/data) datset on Kaggle. The data is stored in a Neo4j database. The database is structured as follows:

### Nodes
- Airport Node: Represents an airport and contains attributes such as:
    - AirportID
    - Name
    - City
    - Country
    - IATA
    - ICAO
    - Latitude
    - Longitude
    - Altitude
    - Timezone
    - DST
    - Tz database time zone
    - Type
    - Source
- Each airport node will be uniquely identified by the IATA code (e.g., "JFK", "LAX").
- Airline Node: Represents an airline and contains attributes such as:
    - AirlineID
    - Name
    - Alias
    - ICAO
    - Callsign
    - Country
    - Active
- Each airline node will be uniquely identified by the IATA code of the airline (e.g., "AA" for American Airlines).
### Relationships (Edges)
- ROUTE Relationship: Represents a flight route between two airports and contains properties such as:
    - Stops: Number of stops on the route (0 for direct flights)
    - Equipment: The aircraft type used on the route
    - Codeshare: Indicates if it's a codeshare route (e.g., "Y" or null)
    - Airline: The airline that operates the route (linked to the Airline node)
    - Example: A ROUTE relationship connects a source airport (e.g., JFK) to a destination airport (e.g., LAX), and the relationship contains the airline's name, number of stops, and aircraft used.
- OPERATES_AT Relationship (Optional): Represents the relationship between an Airline and an Airport showing that the airline operates at the airport. This is not strictly necessary but can be useful for certain queries.
    - Example: An Airline (e.g., AA) operates at a specific Airport (e.g., JFK).



## Source
The data is retrieved from the following sources:
- [Rafiee, Ahmad](https://www.kaggle.com/datasets/ahmadrafiee/airports-airlines-planes-and-routes-update-2024/data) on Kaggle