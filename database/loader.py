from neo4j import GraphDatabase
import pandas as pd
import os
import sys
import time
from io import StringIO
import requests
import certifi
from dotenv import load_dotenv

# Add helper directory to path for distance calculations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "helper"))
from distance import calculate_distance_km

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "airfacts-pw")

# Configuration for batch processing and retries
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))  # Process in batches
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # Retry failed operations
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))  # Seconds between retries

OPENFLIGHTS_BASE_URL = (
    "https://raw.githubusercontent.com/jpatokal/openflights/master/data/"
)
OPENFLIGHTS_DATASETS = {
    "airports": {
        "filename": "airports.dat",
        "columns": [
            "Airport ID",
            "Name",
            "City",
            "Country",
            "IATA",
            "ICAO",
            "Latitude",
            "Longitude",
            "Altitude",
            "Timezone",
            "DST",
            "Tz database time zone",
            "Type",
            "Source",
        ],
        "cypher": "./cypher/load_airport.cypher",
    },
    "airlines": {
        "filename": "airlines.dat",
        "columns": [
            "Airline ID",
            "Name",
            "Alias",
            "IATA",
            "ICAO",
            "Callsign",
            "Country",
            "Active",
        ],
        "cypher": "./cypher/load_airline.cypher",
    },
    "routes": {
        "filename": "routes.dat",
        "columns": [
            "Airline",
            "Airline ID",
            "Source airport",
            "Source airport ID",
            "Destination airport",
            "Destination airport ID",
            "Codeshare",
            "Stops",
            "Equipment",
        ],
        "cypher": "./cypher/load_route.cypher",
    },
}

# Create driver with increased timeout settings
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    connection_timeout=30,  # 30 seconds to establish connection
    max_connection_lifetime=3600,  # 1 hour max connection lifetime
    max_connection_pool_size=50,  # Connection pool size
    connection_acquisition_timeout=60,  # 60 seconds to acquire connection
)


def load_query_from_file(filepath):
    with open(filepath, "r") as file:
        return file.read()


def load_openflights_dataframe(dataset_key):
    config = OPENFLIGHTS_DATASETS[dataset_key]
    url = f"{OPENFLIGHTS_BASE_URL}{config['filename']}"
    response = requests.get(url, timeout=30, verify=certifi.where())
    response.raise_for_status()
    buffer = StringIO(response.content.decode("utf-8", errors="replace"))
    df = pd.read_csv(
        buffer,
        names=config["columns"],
        header=None,
        na_values=["\\N", ""],
        keep_default_na=False,
        dtype=str,
    )
    return df.where(pd.notnull(df), None)


def harmonize_codes(df, primary_col, fallback_col):
    df[primary_col] = df[primary_col].apply(
        lambda value: value.strip().upper() if value else value
    )
    df[fallback_col] = df[fallback_col].apply(
        lambda value: value.strip().upper() if value else value
    )
    df[primary_col] = df[primary_col].fillna(df[fallback_col])
    df[primary_col] = df[primary_col].apply(
        lambda value: value.strip().upper() if value else value
    )
    return df[df[primary_col].notnull() & (df[primary_col] != "")]


def prepare_airports(df):
    df = harmonize_codes(df, "IATA", "ICAO")
    df["Airport ID"] = df["Airport ID"].apply(
        lambda value: value.strip() if value else value
    )
    cleaned = df[df["Airport ID"].notnull()].drop_duplicates(subset=["Airport ID"])
    return cleaned.where(pd.notnull(cleaned), None)


def prepare_airlines(df):
    df = harmonize_codes(df, "IATA", "ICAO")
    df = df[df["Airline ID"].notnull()]
    df["Airline ID"] = df["Airline ID"].apply(
        lambda value: value.strip() if value else value
    )
    df["Active"] = df["Active"].apply(lambda value: value.upper() if value else None)
    cleaned = df.drop_duplicates(subset=["Airline ID"])
    return cleaned.where(pd.notnull(cleaned), None)


def normalize_stops(value):
    if value is None:
        return "0"
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return "0"


def prepare_routes(df, airlines_df, airports_df):
    airline_codes = airlines_df.set_index("Airline ID")["IATA"].to_dict()
    airport_codes = airports_df.set_index("Airport ID")["IATA"].to_dict()

    # Create airport coordinate lookup dictionaries
    airport_coords = airports_df.set_index("IATA")[["Latitude", "Longitude"]].to_dict(
        "index"
    )

    df["Airline"] = df["Airline"].apply(
        lambda value: value.strip().upper() if value else value
    )
    df["Source airport"] = df["Source airport"].apply(
        lambda value: value.strip().upper() if value else value
    )
    df["Destination airport"] = df["Destination airport"].apply(
        lambda value: value.strip().upper() if value else value
    )
    df["Airline ID"] = df["Airline ID"].apply(
        lambda value: value.strip() if value else value
    )
    df["Source airport ID"] = df["Source airport ID"].apply(
        lambda value: value.strip() if value else value
    )
    df["Destination airport ID"] = df["Destination airport ID"].apply(
        lambda value: value.strip() if value else value
    )

    df["Airline"] = df.apply(
        lambda row: (
            row["Airline"] if row["Airline"] else airline_codes.get(row["Airline ID"])
        ),
        axis=1,
    )

    df["Source airport"] = df.apply(
        lambda row: (
            row["Source airport"]
            if row["Source airport"]
            else airport_codes.get(row["Source airport ID"])
        ),
        axis=1,
    )

    df["Destination airport"] = df.apply(
        lambda row: (
            row["Destination airport"]
            if row["Destination airport"]
            else airport_codes.get(row["Destination airport ID"])
        ),
        axis=1,
    )

    df["Stops"] = df["Stops"].apply(normalize_stops)

    filtered = df[
        df["Airline"].notnull()
        & df["Source airport"].notnull()
        & df["Destination airport"].notnull()
    ]

    # Calculate distance for each route
    def calculate_route_distance(row):
        """Calculate distance between source and destination airports"""
        try:
            source_iata = row["Source airport"]
            dest_iata = row["Destination airport"]

            # Get coordinates for both airports
            if source_iata in airport_coords and dest_iata in airport_coords:
                source = airport_coords[source_iata]
                dest = airport_coords[dest_iata]

                # Extract coordinates and convert to float
                src_lat = float(source["Latitude"]) if source["Latitude"] else None
                src_lon = float(source["Longitude"]) if source["Longitude"] else None
                dst_lat = float(dest["Latitude"]) if dest["Latitude"] else None
                dst_lon = float(dest["Longitude"]) if dest["Longitude"] else None

                # Calculate distance if all coordinates are valid
                if all([src_lat, src_lon, dst_lat, dst_lon]):
                    distance = calculate_distance_km(src_lat, src_lon, dst_lat, dst_lon)
                    return round(distance, 2)

            return None
        except (ValueError, TypeError, KeyError):
            return None

    # Add Distance column
    print("Calculating route distances...")
    filtered["Distance"] = filtered.apply(calculate_route_distance, axis=1)

    # Log statistics
    total_routes = len(filtered)
    routes_with_distance = filtered["Distance"].notnull().sum()
    print(f"  Total routes: {total_routes:,}")
    print(
        f"  Routes with distance: {routes_with_distance:,} ({routes_with_distance/total_routes*100:.1f}%)"
    )
    if routes_with_distance > 0:
        avg_distance = filtered["Distance"].mean()
        print(f"  Average distance: {avg_distance:.2f} km")

    return filtered.where(pd.notnull(filtered), None)


def execute_query(dataframe, cypher_file):
    """Execute queries in batches with retry logic"""
    query = load_query_from_file(cypher_file)
    total_records = len(dataframe)
    records = dataframe.to_dict(orient="records")

    print(f"  Processing {total_records:,} records in batches of {BATCH_SIZE}...")

    processed = 0
    failed = 0

    # Process in batches
    for i in range(0, total_records, BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE

        retry_count = 0
        success = False

        while retry_count < MAX_RETRIES and not success:
            try:
                with driver.session() as session:
                    for record in batch:
                        session.run(query, record)

                processed += len(batch)
                print(
                    f"  ✓ Batch {batch_num}/{total_batches} completed ({processed:,}/{total_records:,})"
                )
                success = True

            except Exception as e:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print(
                        f"  ⚠ Batch {batch_num} failed (attempt {retry_count}/{MAX_RETRIES}): {str(e)[:100]}"
                    )
                    print(f"  ⏳ Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(
                        f"  ✗ Batch {batch_num} failed after {MAX_RETRIES} attempts: {str(e)[:100]}"
                    )
                    failed += len(batch)

    if failed > 0:
        print(f"  ⚠ Warning: {failed:,} records failed to upload")

    return processed, failed


def test_connection():
    """Test Neo4j connection before starting data load"""
    print("Testing Neo4j connection...")
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        print("✓ Connection successful!")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Check if Neo4j is running")
        print("  2. Verify NEO4J_URI in .env file")
        print("  3. Check username and password")
        print("  4. For AuraDB, ensure you have internet connectivity")
        return False


if __name__ == "__main__":
    try:
        # Test connection first
        if not test_connection():
            print("\n❌ Aborting due to connection failure")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("Starting data upload...")
        print("=" * 70)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        print("\nLoading and preparing data...")
        airports_df = prepare_airports(load_openflights_dataframe("airports"))
        print(f"  ✓ Airports: {len(airports_df):,} records prepared")

        airlines_df = prepare_airlines(load_openflights_dataframe("airlines"))
        print(f"  ✓ Airlines: {len(airlines_df):,} records prepared")

        routes_df = prepare_routes(
            load_openflights_dataframe("routes"), airlines_df, airports_df
        )
        print(f"  ✓ Routes: {len(routes_df):,} records prepared")

        print("\n" + "=" * 70)
        print("Uploading Airports...")
        print("=" * 70)
        processed, failed = execute_query(
            airports_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["airports"]["cypher"]),
        )

        print("\n" + "=" * 70)
        print("Uploading Airlines...")
        print("=" * 70)
        processed, failed = execute_query(
            airlines_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["airlines"]["cypher"]),
        )

        print("\n" + "=" * 70)
        print("Uploading Routes...")
        print("=" * 70)
        processed, failed = execute_query(
            routes_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["routes"]["cypher"]),
        )

        print("\n" + "=" * 70)
        print("✅ Data upload completed successfully!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠ Upload interrupted by user")
    except Exception as exc:
        print(f"\n❌ An error occurred: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        print("\nClosing database connection...")
        driver.close()
        print("Done.")
