from neo4j import GraphDatabase
import pandas as pd
import os

# Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "airfacts-pw"

driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to update distances in ROUTE relationships
def update_route_distance(tx, source, destination, airline, distance):
    query = """
    MATCH (source:Airport {IATA: $source}),
          (destination:Airport {IATA: $destination}),
          (source)-[r:ROUTE {Airline: $airline}]->(destination)
    SET r.Distance = $distance
    """
    tx.run(query, source=source, destination=destination, airline=airline, distance=distance)

def main():
    # Load CSV data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    routes_with_distances_csv = os.path.join(base_dir, "../datasets/routes_with_distances.csv")
    routes_df = pd.read_csv(routes_with_distances_csv)

    # Drop rows with missing distances
    routes_df.dropna(subset=["Distance"], inplace=True)

    with driver.session() as session:
        for _, row in routes_df.iterrows():
            source = row["Source airport"]
            destination = row["Destination airport"]
            airline = row["Airline"]
            distance = row["Distance"]

            if distance is not None:  # Update only if distance is provided
                session.write_transaction(update_route_distance, source, destination, airline, float(distance))

    print("Routes with distances updated successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()
