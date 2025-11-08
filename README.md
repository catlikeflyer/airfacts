# Airfacts API

A simple, open-source API that provides information about airports, airlines, and flight routes worldwide.

## Background

This project originates from my interest in aviation and an attempt to provide accessible data related to aviation facts. While robust APIs exist, they are often not available for free. By using FastAPI and a Neo4j database, this project serves as an open-source alternative to retrieve information about airports, airlines, and routes.

## Features

- 🛫 **Airports**: Search airports by IATA code, city, or country
- ✈️ **Airlines**: Get airline information by IATA code or country
- 🗺️ **Routes**: Find flight routes between airports
- 📊 **Real-time Data**: Data fetched from OpenFlights
- 🚀 **Fast API**: Built with FastAPI for high performance
- 📝 **Auto Documentation**: Interactive API docs at `/docs`
- 🎨 **Dashboard**: Interactive Streamlit dashboard for data visualization

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Docker (for Neo4j database)
- Git

### Easy Setup (macOS/Linux)

**Option 1: Using the automated script**

```bash
chmod +x start.sh
./start.sh
```

**Option 2: Using Make commands**

```bash
make all      # Complete setup
make start    # Start the API server
```

Run `make help` to see all available commands.

These automated tools will:

- Create a virtual environment
- Install all dependencies
- Start Neo4j in Docker
- Optionally load data from OpenFlights
- Start the API server

### Manual Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/catlikeflyer/airfacts.git
   cd airfacts
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements-minimal.txt
   ```

4. **Set up Neo4j Database**

   Choose one of the following options:

   **Option A: Using Docker (Recommended)**

   ```bash
   docker run --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -d \
     -v $HOME/neo4j/data:/data \
     -v $HOME/neo4j/logs:/logs \
     -v $HOME/neo4j/import:/var/lib/neo4j/import \
     -v $HOME/neo4j/plugins:/plugins \
     --env NEO4J_AUTH=neo4j/airfacts-pw \
     neo4j:latest
   ```

   **Option B: Using Neo4j Desktop**

   - Download and install [Neo4j Desktop](https://neo4j.com/download/)
   - Create a new database
   - Set username to `neo4j` and password to `airfacts-pw`
   - Start the database on `bolt://localhost:7687`

5. **Load data into Neo4j**

   ```bash
   cd neo4j
   python3 loader.py
   ```

   This will fetch data from OpenFlights and populate your Neo4j database. This may take a few minutes.

6. **Run the API**

   ```bash
   cd ../api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**

   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

8. **(Optional) Run the Dashboard**
   ```bash
   cd ../dashboard
   pip install -r requirements.txt
   streamlit run app.py
   ```
   - Dashboard: http://localhost:8501

## Usage Examples

### Get all airports (with pagination)

```bash
curl "http://localhost:8000/api/airports/?limit=10&skip=0"
```

### Get a specific airport by IATA code

```bash
curl "http://localhost:8000/api/airports/JFK"
```

### Get airports in a specific country

```bash
curl "http://localhost:8000/api/airports/country/United%20States"
```

### Get all airlines

```bash
curl "http://localhost:8000/api/airlines/?limit=10"
```

### Get routes from an airport

```bash
curl "http://localhost:8000/api/routes/source/JFK"
```

### Get routes between two airports

```bash
curl "http://localhost:8000/api/routes/source/JFK/destination/LAX"
```

## API Endpoints

### Airports

- `GET /api/airports/` - Get all airports (paginated)
- `GET /api/airports/{iata}` - Get airport by IATA code
- `GET /api/airports/country/{country}` - Get airports by country

### Airlines

- `GET /api/airlines/` - Get all airlines (paginated)
- `GET /api/airlines/{iata}` - Get airline by IATA code
- `GET /api/airlines/country/{country}` - Get airlines by country

### Routes

- `GET /api/routes/source/{iata}` - Get routes from an airport
- `GET /api/routes/destination/{iata}` - Get routes to an airport
- `GET /api/routes/source/{source}/destination/{dest}` - Get routes between two airports
- `GET /api/routes/airline/{iata}` - Get all routes for an airline

For detailed schema information, see [API_SCHEMAS.md](API_SCHEMAS.md)

## Database Structure

The project uses a Neo4j database. To run the database, you need to have Docker installed.

### Database Schema

The data is fetched directly from [OpenFlights](https://openflights.org/data.html) and stored in a Neo4j database. The database is structured as follows:

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

## Development

### Project Structure

```
airfacts/
├── api/                      # FastAPI application
│   ├── main.py              # Main application entry point
│   ├── database.py          # Neo4j connection
│   ├── schemas.py           # Pydantic models
│   └── routers/             # API route handlers
│       ├── airports.py
│       ├── airlines.py
│       └── routes.py
├── neo4j/                   # Database related files
│   ├── loader.py            # Data loading script
│   ├── Dockerfile           # Neo4j container config
│   └── cypher/              # Cypher query files
│       ├── load_airport.cypher
│       ├── load_airline.cypher
│       └── load_route.cypher
├── requirements-minimal.txt  # Python dependencies
└── README.md                # This file
```

### Running in Development Mode

Start the API with auto-reload on code changes:

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

The application uses environment variables for configuration. You can set them using a `.env` file in the project root.

**Create a `.env` file:**

```bash
cp .env.example .env
```

**Edit `.env` with your configuration:**

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=airfacts-pw
```

Alternatively, you can export environment variables in your shell:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="airfacts-pw"
```

The application automatically loads variables from `.env` using python-dotenv.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

Having issues? Check out the [Troubleshooting Guide](TROUBLESHOOTING.md) for common problems and solutions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Data Source

The data is retrieved from the following source:

- [OpenFlights](https://openflights.org/data.html) - Airport, airline, and route data
