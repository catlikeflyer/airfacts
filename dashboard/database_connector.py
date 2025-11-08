from neo4j import GraphDatabase
import os
from typing import List, Dict, Any, Optional


class Neo4jConnector:
    """Connector for Neo4j database operations"""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "airfacts-pw")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()

    def execute_query(
        self, query: str, parameters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results as a list of dictionaries"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    # ===== Statistics Queries =====

    def get_total_airports(self) -> int:
        """Get total number of airports"""
        query = "MATCH (a:Airport) RETURN count(a) as count"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_total_airlines(self) -> int:
        """Get total number of airlines"""
        query = "MATCH (a:Airline) RETURN count(a) as count"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_total_routes(self) -> int:
        """Get total number of routes"""
        query = "MATCH ()-[r:ROUTE]->() RETURN count(r) as count"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_total_countries(self) -> int:
        """Get total number of countries with airports"""
        query = "MATCH (a:Airport) RETURN count(DISTINCT a.Country) as count"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    # ===== Airport Queries =====

    def search_airports(
        self, search_term: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search airports by name, city, country, or IATA code"""
        query = """
        MATCH (a:Airport)
        WHERE toLower(a.Name) CONTAINS toLower($search)
           OR toLower(a.City) CONTAINS toLower($search)
           OR toLower(a.Country) CONTAINS toLower($search)
           OR toLower(a.IATA) = toLower($search)
        RETURN a.IATA as IATA, a.Name as Name, a.City as City, 
               a.Country as Country, a.Latitude as Latitude, 
               a.Longitude as Longitude, a.Altitude as Altitude
        LIMIT $limit
        """
        return self.execute_query(query, {"search": search_term, "limit": limit})

    def get_airport_by_iata(self, iata: str) -> Optional[Dict[str, Any]]:
        """Get detailed airport information by IATA code"""
        query = """
        MATCH (a:Airport {IATA: $iata})
        RETURN a.IATA as IATA, a.Name as Name, a.City as City, 
               a.Country as Country, a.ICAO as ICAO,
               a.Latitude as Latitude, a.Longitude as Longitude,
               a.Altitude as Altitude, a.Timezone as Timezone,
               a.DST as DST, a.`Tz database time zone` as TzDatabase,
               a.Type as Type, a.Source as Source
        """
        result = self.execute_query(query, {"iata": iata.upper()})
        return result[0] if result else None

    def get_airports_by_country(
        self, country: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all airports in a specific country"""
        query = """
        MATCH (a:Airport {Country: $country})
        RETURN a.IATA as IATA, a.Name as Name, a.City as City,
               a.Latitude as Latitude, a.Longitude as Longitude
        LIMIT $limit
        """
        return self.execute_query(query, {"country": country, "limit": limit})

    def get_all_airports_for_map(self, limit: int = 5000) -> List[Dict[str, Any]]:
        """Get all airports with coordinates for mapping"""
        query = """
        MATCH (a:Airport)
        WHERE a.Latitude IS NOT NULL AND a.Longitude IS NOT NULL
        RETURN a.IATA as IATA, a.Name as Name, a.City as City,
               a.Country as Country, a.Latitude as Latitude, 
               a.Longitude as Longitude
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    # ===== Route Queries =====

    def get_routes_from_airport(
        self, iata: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all routes departing from an airport"""
        query = """
        MATCH (source:Airport {IATA: $iata})-[r:ROUTE]->(dest:Airport)
        RETURN source.IATA as source, dest.IATA as destination,
               dest.Name as dest_name, dest.City as dest_city,
               dest.Country as dest_country, r.Airline as airline,
               r.Distance as distance
        ORDER BY r.Distance
        LIMIT $limit
        """
        return self.execute_query(query, {"iata": iata.upper(), "limit": limit})

    def get_routes_between_airports(
        self, source: str, destination: str
    ) -> List[Dict[str, Any]]:
        """Get all routes between two airports"""
        query = """
        MATCH (source:Airport {IATA: $source})-[r:ROUTE]->(dest:Airport {IATA: $destination})
        RETURN source.IATA as source, source.Name as source_name,
               dest.IATA as destination, dest.Name as dest_name,
               r.Airline as airline, r.Distance as distance,
               r.Stops as stops, r.Equipment as equipment
        ORDER BY r.Distance
        """
        return self.execute_query(
            query, {"source": source.upper(), "destination": destination.upper()}
        )

    def get_route_with_coordinates(
        self, source: str, destination: str
    ) -> Optional[Dict[str, Any]]:
        """Get route information with coordinates for mapping"""
        query = """
        MATCH (source:Airport {IATA: $source})-[r:ROUTE]->(dest:Airport {IATA: $destination})
        RETURN source.IATA as source_iata, source.Name as source_name,
               source.Latitude as source_lat, source.Longitude as source_lon,
               dest.IATA as dest_iata, dest.Name as dest_name,
               dest.Latitude as dest_lat, dest.Longitude as dest_lon,
               r.Airline as airline, r.Distance as distance
        LIMIT 1
        """
        result = self.execute_query(
            query, {"source": source.upper(), "destination": destination.upper()}
        )
        return result[0] if result else None

    # ===== Analytics Queries =====

    def get_top_airports_by_routes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get airports with most outgoing routes"""
        query = """
        MATCH (a:Airport)-[r:ROUTE]->()
        RETURN a.IATA as IATA, a.Name as Name, a.City as City,
               a.Country as Country, count(r) as route_count
        ORDER BY route_count DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_top_airlines_by_routes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get airlines operating the most routes"""
        query = """
        MATCH ()-[r:ROUTE]->()
        WHERE r.Airline IS NOT NULL
        WITH r.Airline as airline, count(r) as route_count
        MATCH (a:Airline {IATA: airline})
        RETURN a.IATA as IATA, a.Name as Name, a.Country as Country,
               route_count
        ORDER BY route_count DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_countries_by_airport_count(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Get countries with most airports"""
        query = """
        MATCH (a:Airport)
        WHERE a.Country IS NOT NULL
        RETURN a.Country as country, count(a) as airport_count
        ORDER BY airport_count DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_all_countries(self) -> List[str]:
        """Get list of all countries"""
        query = """
        MATCH (a:Airport)
        WHERE a.Country IS NOT NULL
        RETURN DISTINCT a.Country as country
        ORDER BY country
        """
        result = self.execute_query(query)
        return [r["country"] for r in result]
