"""
Neo4j Database Connection Checker

This script checks the connection to the Neo4j database and displays basic information.
"""

from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
import sys

# Load environment variables from .env file
load_dotenv()

# Get Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "airfacts-pw")


def check_connection():
    """Check connection to Neo4j database and display stats."""
    print("=" * 60)
    print("Neo4j Database Connection Check")
    print("=" * 60)
    print(f"\nConnection Details:")
    print(f"  URI:      {NEO4J_URI}")
    print(f"  User:     {NEO4J_USERNAME}")
    print(f"  Password: {'*' * len(NEO4J_PASSWORD)}")
    print()

    driver = None
    try:
        # Attempt to connect
        print("Connecting to Neo4j...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

        # Verify connectivity
        driver.verify_connectivity()
        print("✓ Connection successful!\n")

        # Get database statistics
        with driver.session() as session:
            print("Database Statistics:")
            print("-" * 60)

            # Count airports
            result = session.run("MATCH (a:Airport) RETURN count(a) as count")
            airport_count = result.single()["count"]
            print(f"  Airports:  {airport_count:,}")

            # Count airlines
            result = session.run("MATCH (a:Airline) RETURN count(a) as count")
            airline_count = result.single()["count"]
            print(f"  Airlines:  {airline_count:,}")

            # Count routes
            result = session.run("MATCH ()-[r:ROUTE]->() RETURN count(r) as count")
            route_count = result.single()["count"]
            print(f"  Routes:    {route_count:,}")

            print("-" * 60)

            # Get sample data
            print("\nSample Airport:")
            result = session.run(
                """
                MATCH (a:Airport)
                WHERE a.iata_code IS NOT NULL
                RETURN a.name as name, a.iata_code as iata, 
                       a.city as city, a.country as country
                LIMIT 1
            """
            )
            record = result.single()
            if record:
                print(f"  {record['name']} ({record['iata']})")
                print(f"  {record['city']}, {record['country']}")

            print("\nSample Airline:")
            result = session.run(
                """
                MATCH (a:Airline)
                WHERE a.iata_code IS NOT NULL
                RETURN a.name as name, a.iata_code as iata, 
                       a.country as country
                LIMIT 1
            """
            )
            record = result.single()
            if record:
                print(f"  {record['name']} ({record['iata']})")
                print(f"  {record['country']}")

            print("\nSample Route:")
            result = session.run(
                """
                MATCH (src:Airport)-[r:ROUTE]->(dst:Airport)
                WHERE src.iata_code IS NOT NULL AND dst.iata_code IS NOT NULL
                RETURN src.iata_code as src, dst.iata_code as dst, 
                       r.airline as airline
                LIMIT 1
            """
            )
            record = result.single()
            if record:
                print(f"  {record['src']} → {record['dst']}")
                print(f"  Airline: {record['airline']}")

        print("\n" + "=" * 60)
        print("✓ Database is healthy and contains data!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Connection failed!")
        print(f"Error: {str(e)}\n")
        print("Troubleshooting:")
        print("  1. Ensure Neo4j is running: docker ps | grep neo4j")
        print("  2. Check your .env file has correct credentials")
        print("  3. Verify Neo4j is accessible at the specified URI")
        print("  4. Try loading data: python3 loader.py")
        print("=" * 60)
        return False

    finally:
        if driver:
            driver.close()


if __name__ == "__main__":
    success = check_connection()
    sys.exit(0 if success else 1)
