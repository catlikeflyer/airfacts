# Airfacts Dashboard 📊

Interactive Streamlit dashboard to explore global aviation data from the Airfacts Neo4j database.

## Features

### Phase 1 (MVP) ✅ Complete

#### 🏠 Home

- Database statistics overview
- Top airports and countries visualizations
- Quick start guide

#### 🔍 Airport Search

- Search airports by name, city, country, or IATA code
- View detailed airport information
- See routes from each airport
- Interactive airport location maps

#### 🗺️ Route Explorer

- Find routes between any two airports
- Visualize routes on interactive maps
- View all airports on a global map
- Filter by country

#### 📊 Analytics

- Top airports by connectivity
- Top airlines by route count
- Country-level airport distribution
- Route distance analytics
- Interactive charts and visualizations

### Phase 2 🚧 Work in Progress

- ✅ Airline route networks on map
- ✅ Top N airports/airlines charts
- 🚧 Distance-based filtering
- 🚧 Graph visualization

### Phase 3 📋 Planned

- 📋 Shortest path algorithm visualization
- 📋 Network graph of airport connections
- 📋 Airline route network comparison
- 📋 Export data to CSV
- 📋 Advanced filtering options
- 📋 Real-time search suggestions

## Installation

1. **Install dependencies:**

   ```bash
   cd dashboard
   pip install -r requirements.txt
   ```

2. **Ensure Neo4j is running:**

   ```bash
   docker ps | grep neo4j
   ```

   If not running, start it:

   ```bash
   cd ..
   make start-neo4j
   ```

3. **Load data (if not already done):**
   ```bash
   cd ../database
   python3 loader.py
   ```

## Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

The dashboard will open in your browser at http://localhost:8501

## Configuration

The dashboard connects to Neo4j using environment variables. You can set them using a `.env` file in the project root.

**Create a `.env` file:**

```bash
cd ..  # Go to project root
cp .env.example .env
```

**Edit `.env` with your configuration:**

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=airfacts-pw
```

Alternatively, you can export environment variables in your shell (they will use these defaults if not set):

- `NEO4J_URI` - Default: `bolt://localhost:7687`
- `NEO4J_USERNAME` - Default: `neo4j`
- `NEO4J_PASSWORD` - Default: `airfacts-pw`

## Usage Examples

### Search for an Airport

1. Go to "🔍 Airport Search"
2. Enter "JFK" or "London" or "United States"
3. Select an airport from results to see details

### Find a Route

1. Go to "🗺️ Route Explorer"
2. Enter source airport: `JFK`
3. Enter destination airport: `LAX`
4. Click "Find Routes" to see available routes on a map

### Explore Analytics

1. Go to "📊 Analytics"
2. Explore different tabs for airports, airlines, and routes
3. Adjust sliders to see more/fewer results
4. View interactive charts and data tables

## Project Structure

```
dashboard/
├── app.py                      # Main Streamlit app
├── database_connector.py       # Neo4j database connector
├── requirements.txt            # Python dependencies
├── pages/                      # Page modules
│   ├── __init__.py
│   ├── home.py                # Home page
│   ├── airport_search.py      # Airport search functionality
│   ├── route_explorer.py      # Route finding and visualization
│   └── analytics.py           # Analytics dashboards
└── README.md                  # This file
```

## Technologies Used

- **Streamlit** - Dashboard framework
- **Plotly** - Interactive visualizations
- **Neo4j** - Graph database
- **Pandas** - Data manipulation

## Tips

- Use the sidebar to navigate between different sections
- All searches are case-insensitive
- Click on interactive charts to zoom and explore
- Expand data tables to see full details
- Use browser back button if needed (Streamlit maintains state)

## Troubleshooting

**Dashboard won't start:**

- Ensure streamlit is installed: `pip install streamlit`
- Check you're in the dashboard directory

**No data showing:**

- Verify Neo4j is running: `docker ps | grep neo4j`
- Ensure data is loaded: Check Neo4j browser at http://localhost:7474
- Run loader: `cd ../database && python3 loader.py`

**Connection error:**

- Check Neo4j credentials match environment variables
- Verify Neo4j is accessible at bolt://localhost:7687

---

Made with ❤️ using Streamlit & Neo4j
