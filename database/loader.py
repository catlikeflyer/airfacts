from neo4j import GraphDatabase
import pandas as pd
import os
from io import StringIO
import requests
import certifi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "airfacts-pw")

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

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


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
    return filtered.where(pd.notnull(filtered), None)


def execute_query(dataframe, cypher_file):
    query = load_query_from_file(cypher_file)
    with driver.session() as session:
        for record in dataframe.to_dict(orient="records"):
            session.run(query, record)


if __name__ == "__main__":
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        airports_df = prepare_airports(load_openflights_dataframe("airports"))
        airlines_df = prepare_airlines(load_openflights_dataframe("airlines"))
        routes_df = prepare_routes(
            load_openflights_dataframe("routes"), airlines_df, airports_df
        )

        print("Uploading Airports...")
        execute_query(
            airports_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["airports"]["cypher"]),
        )

        print("Uploading Airlines...")
        execute_query(
            airlines_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["airlines"]["cypher"]),
        )

        print("Uploading Routes...")
        execute_query(
            routes_df,
            os.path.join(base_dir, OPENFLIGHTS_DATASETS["routes"]["cypher"]),
        )

        print("Data upload completed successfully!")
    except Exception as exc:
        print(f"An error occurred: {exc}")
    finally:
        driver.close()
