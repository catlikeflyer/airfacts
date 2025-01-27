from neo4j import GraphDatabase
import pandas as pd
import os

# Connect to Neo4j
uri = "bolt://localhost:7687"  # URI to Docker container, local
username = "neo4j"
password = "airfacts-pw"

driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to read Cypher queries from file
def load_query_from_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

# Function to execute Cypher queries
def execute_query(csv_path, cypher_file):
    query = load_query_from_file(cypher_file)
    df = pd.read_csv(csv_path)

    # If Nan values are present, replace them with "N"
    df.fillna("N", inplace=True)

    with driver.session() as session:
        for _, row in df.iterrows():
            session.run(query, row.to_dict())

# Main Script
if __name__ == "__main__":
    try:
        # File paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        airports_csv = os.path.join(base_dir, "../datasets/airports.csv")
        airlines_csv = os.path.join(base_dir, "../datasets/airlines.csv")
        routes_csv = os.path.join(base_dir, "../datasets/routes.csv")

        airports_cypher = os.path.join(base_dir, "./cypher/load_airport.cypher")
        airlines_cypher = os.path.join(base_dir, "./cypher/load_airline.cypher")
        routes_cypher = os.path.join(base_dir, "./cypher/load_route.cypher")

        print("Uploading Airports...")
        execute_query(airports_csv, airports_cypher)

        print("Uploading Airlines...")
        execute_query(airlines_csv, airlines_cypher)

        print("Uploading Routes...")
        execute_query(routes_csv, routes_cypher)

        print("Data upload completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()
