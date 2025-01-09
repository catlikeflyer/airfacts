from neo4j import GraphDatabase
import pandas as pd

# Connect to Neo4j
uri = "https://localhost:7687"  # URI to Docker container
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

    with driver.session() as session:
        for _, row in df.iterrows():
            session.run(query, row.to_dict())

# Main Script
if __name__ == "__main__":
    try:
        # File paths
        airports_csv = "../datasets/airports.csv"
        airlines_csv = "../datasets/airlines.csv"
        routes_csv = "../datasets/routes.csv"

        airports_cypher = "./load_airport.cypher"
        airlines_cypher = "./load_airline.cypher"
        routes_cypher = "./load_route.cypher"

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
